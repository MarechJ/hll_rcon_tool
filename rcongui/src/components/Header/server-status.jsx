import React, { useState, useEffect } from "react";
import "react-toastify/dist/ReactToastify.css";
import { get, handle_http_errors, showResponse } from "../../utils/fetchUtils";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import Link from "@mui/material/Link";
import { fromJS, List } from "immutable";
import { Box, IconButton, Typography } from "@mui/material";
import SwapVertIcon from '@mui/icons-material/SwapVert';
import { styled } from "@mui/material/styles";

const Wrapper = styled('div')(({ theme }) => ({
  paddingLeft: theme.spacing(1),
}));

const MenuBox = styled('div')(({ theme }) => ({
  display: "flex",
  gap: theme.spacing(1),
}));

const ServerStatus = () => {
  const [anchorEl, setAnchorEl] = useState(null);
  const [name, setName] = useState("");
  const [numCurrentPlayers, setNumCurrentPlayers] = useState(0);
  const [maxPlayers, setMaxPlayers] = useState(0);
  const [map, setMap] = useState(null);
  const [serverList, setServerList] = useState(List());
  const [timeRemaining, setTimeRemaining] = useState("0:00:00");
  const [balance, setBalance] = useState("0vs0");
  const [score, setScore] = useState("0:0");

  const refreshIntervalSec = 10;
  const listRefreshIntervalSec = 30;

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const load = async () => {
    return get(`get_status`)
      .then((response) => showResponse(response, "get_status", false))
      .then((data) => {
        setName(data?.result.name);
        setMap(data?.result.map);
        setNumCurrentPlayers(data.result.current_players);
        setMaxPlayers(data.result.max_players);
        document.title = `(${data?.result.current_players}) ${data?.result.short_name}`;
      })
      .catch(handle_http_errors);
  };

  const loadInfo = async () => {
    return get(`get_gamestate`)
      .then((response) => showResponse(response, "get_gamestate", false))
      .then((data) => {
        setBalance(
          `${data.result.num_allied_players}vs${data.result.num_axis_players}`
        );
        setScore(`${data.result.allied_score}:${data.result.axis_score}`);
        setTimeRemaining(data.result.raw_time_remaining);
      })
      .catch(handle_http_errors);
  };

  const loadServerList = async () => {
    return get(`get_server_list`)
      .then((response) => showResponse(response, "get_server_list", false))
      .then((data) => {
        setServerList(fromJS(data.result || []));
      })
      .catch(handle_http_errors);
  };

  useEffect(() => {
    load();
    const interval = setInterval(load, refreshIntervalSec * 1000);
    const intervalLoadList = setInterval(() => {
      loadServerList();
      loadInfo();
    }, listRefreshIntervalSec * 1000);

    loadServerList();
    loadInfo();

    return () => {
      clearInterval(interval);
      clearInterval(intervalLoadList);
    };
  }, []);

  return (
    (<Wrapper>
      <MenuBox>
        <Typography variant="subtitle2" component={"span"} color="inherit">
          {name}
        </Typography>
        {!!serverList.size && (
          <IconButton
            onClick={handleClick}
            aria-label="select server"
            size="small"
          >
            <SwapVertIcon fontSize="inherit" />
          </IconButton>
        )}
      </MenuBox>
      <Menu
        id="simple-menu"
        anchorEl={anchorEl}
        keepMounted
        open={Boolean(anchorEl)}
        onClose={handleClose}
      >
        {serverList.map((s) => {
          let link = "";
          if (s.get("link")) {
            link = new URL(`${s.get("link")}${window.location.hash}`);
          } else {
            const regex = /:(\d+)/gm;
            link = new URL(
              window.location.href.replace(regex, `:${s.get("port")}`)
            );
          }
          return (
            <MenuItem onClick={handleClose} key={s.get("name")}>
              <Link color="inherit" href={link}>
                {s.get("name")}
              </Link>
            </MenuItem>
          );
        })}
      </Menu>
      <Typography variant="caption">
        {numCurrentPlayers}/{maxPlayers} ({balance}) -{" "}
        {map?.pretty_name ?? "Unknown Map"} - {timeRemaining} - {score}
      </Typography>
    </Wrapper>)
  );
};

export default ServerStatus;
