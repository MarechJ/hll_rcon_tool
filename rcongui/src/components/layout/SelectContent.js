import { useMemo, useCallback } from "react";
import MuiAvatar from "@mui/material/Avatar";
import MuiListItemAvatar from "@mui/material/ListItemAvatar";
import MenuItem from "@mui/material/MenuItem";
import ListItemText from "@mui/material/ListItemText";
import ListSubheader from "@mui/material/ListSubheader";
import Select, { selectClasses } from "@mui/material/Select";
import { styled } from "@mui/material/styles";
import DevicesRoundedIcon from "@mui/icons-material/DevicesRounded";
import { useGlobalStore } from "@/stores/global-state";
import { useNavigate } from 'react-router-dom';

const Avatar = styled(MuiAvatar)(({ theme }) => ({
  width: 28,
  height: 28,
  backgroundColor: theme.palette.background.paper,
  color: theme.palette.text.secondary,
  border: `1px solid ${theme.palette.divider}`,
}));

const ListItemAvatar = styled(MuiListItemAvatar)({
  minWidth: 0,
  marginRight: 12,
});

/**
 * Builds a URL for navigating to a different server while preserving current path/query/hash
 */
function buildServerUrl(selectedServer, currentLocation) {
  let newUrl;

  if (selectedServer.link) {
    // Server has explicit link - use it as base
    newUrl = new URL(selectedServer.link);
    newUrl.pathname = currentLocation.pathname;
    newUrl.search = currentLocation.search;
    newUrl.hash = currentLocation.hash;
  } else {
    // No explicit link - replace port in current URL
    const portRegex = /:(\d+)/gm;
    const urlWithNewPort = currentLocation.href.replace(portRegex, `:${selectedServer.port}`);
    newUrl = new URL(urlWithNewPort);
  }

  return newUrl;
}

export default function SelectContent() {
  const thisServer = useGlobalStore((state) => state.serverState);
  const otherServers = useGlobalStore((state) => state.servers);
  const navigate = useNavigate();

  const servers = useMemo(() => {
    return thisServer ? [thisServer, ...otherServers] : null;
  }, [thisServer, otherServers]);

  const handleChange = useCallback((event) => {
    if (!servers) return;

    const serverNumber = Number(event.target.value);
    const selectedServer = servers.find(
      (server) => server.server_number === serverNumber
    );

    if (!selectedServer) {
      return;
    }

    const newUrl = buildServerUrl(selectedServer, window.location);

    if (newUrl.origin === window.location.origin) {
      navigate(newUrl.pathname + newUrl.search + newUrl.hash, { replace: true });
    } else {
      window.location.replace(newUrl.href);
    }
  }, [servers, navigate]);

  const hasOnlyOneServer = useMemo(() => {
    return servers && servers.length === 1;
  }, [servers]);

  return (
    <Select
      labelId="server-select"
      id="server-simple-select"
      value={thisServer?.server_number ?? ""}
      onChange={handleChange}
      displayEmpty
      inputProps={{ "aria-label": "Select server" }}
      fullWidth
      disabled={hasOnlyOneServer}
      MenuProps={{
        PaperProps: {
          sx: {
            "& .MuiMenuItem-root:not(:last-child)": {
              mb: 1,
            },
          },
        },
      }}
      sx={{
        maxHeight: 56,
        "&.MuiList-root": {
          p: "8px",
        },
        [`& .${selectClasses.select}`]: {
          display: "flex",
          alignItems: "center",
          gap: "2px",
          pl: 1,
        },
      }}
    >
      <ListSubheader sx={{ pt: 0 }}>Servers</ListSubheader>
      {servers ? (
        servers.map((server) => (
          <MenuItem key={server.server_number} value={server.server_number}>
            <ListItemAvatar>
              <Avatar alt={server.name ?? "<server_name>"}>
                <DevicesRoundedIcon sx={{ fontSize: "1rem" }} />
              </Avatar>
            </ListItemAvatar>
            <ListItemText
              sx={{
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}
              primary={server.name ?? "<server_name>"}
              secondary={
                `Server - ${server.server_number}` ?? "<server_number>"
              }
            />
          </MenuItem>
        ))
      ) : (
        <MenuItem value={""}>
          <ListItemAvatar>
            <Avatar alt={"?"}>
              <DevicesRoundedIcon sx={{ fontSize: "1rem" }} />
            </Avatar>
          </ListItemAvatar>
          <ListItemText
            sx={{
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
            primary={"Loading..."}
            secondary={"..."}
          />
        </MenuItem>
      )}
    </Select>
  );
}
