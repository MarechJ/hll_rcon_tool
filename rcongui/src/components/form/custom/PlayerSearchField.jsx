import React, { useEffect, useMemo, useRef, useState } from "react";
import { debounce } from "lodash";
import { cmd } from "@/utils/fetchUtils";
import Typography from "@mui/material/Typography";
import {
  Avatar,
  Box,
  ClickAwayListener,
  Paper,
  Popper,
  TextField,
  Stack,
  Tooltip,
  IconButton,
} from "@mui/material";
import { styled } from "@mui/material/styles";
import { AddCircleOutline } from "@mui/icons-material";

const SuggestionsList = styled(Paper)(({ theme }) => ({
  maxHeight: 300,
  overflow: "auto",
  marginTop: theme.spacing(1),
}));

const SuggestionItem = styled(Box)(({ theme }) => ({
  padding: theme.spacing(1),
  display: "flex",
  alignItems: "center",
  cursor: "pointer",
  "&:hover": {
    backgroundColor: theme.palette.action.hover,
  },
}));

export default function PlayerSearchField({
  onSelect,
  disableAddBtn = false,
  ...props
}) {
  const [suggestions, setSuggestions] = useState([]);
  const [anchorEl, setAnchorEl] = useState(null);
  const [isOpen, setIsOpen] = useState(false);
  const [nameInputValue, setNameInputValue] = useState("");
  const [idInputValue, setIdInputValue] = useState("");

  const nameInputRef = useRef(null);
  const idInputRef = useRef(null);
  const nameRef = useRef(nameInputValue);
  const idRef = useRef(idInputValue);

  useEffect(() => {
    debouncedFetchSuggestions();
    nameRef.current = nameInputValue;
  }, [nameInputValue]);

  useEffect(() => {
    debouncedFetchSuggestions();
    idRef.current = idInputValue;
  }, [idInputValue]);

  const fetchSuggestions = async () => {
    setSuggestions([]);

    if (!nameRef.current && !idRef.current) {
      setIsOpen(false);
      return;
    }

    const params = {
      payload: {
        page_size: 15,
        page: 1,
        player_name: nameRef.current,
        player_id: idRef.current,
        ignore_accent: true,
      },
    };

    const response = await cmd.GET_PLAYERS_RECORDS(params);
    if (response?.result?.failed) {
      return;
    }
    setSuggestions(response.result.players);
    setIsOpen(true);
  };

  const debouncedFetchSuggestions = useMemo(
    () => debounce(fetchSuggestions, 600),
    []
  );

  const handleInputChange = (event) => {
    const value = event.target.value;
    if (event.target.name === "hll_player_name") {
      setNameInputValue(value);
      setAnchorEl(nameInputRef.current);
    } else {
      setIdInputValue(value);
      setAnchorEl(idInputRef.current);
    }
  };

  const handlePlayerSelect = (selectedPlayer) => {
    onSelect(selectedPlayer);
    setNameInputValue("");
    setIdInputValue("");
    setIsOpen(false);
  };

  const handleClickAway = () => {
    setIsOpen(false);
  };

  return (
    <ClickAwayListener onClickAway={handleClickAway}>
      <Stack spacing={1} direction={"row"} alignItems={"center"} {...props}>
        <TextField
          ref={nameInputRef}
          fullWidth
          label={"Name"}
          value={nameInputValue}
          name="hll_player_name"
          onChange={handleInputChange}
          type={"search"}
          placeholder={"Enter player name"}
        />
        <TextField
          ref={idInputRef}
          fullWidth
          label={"Player ID"}
          value={idInputValue}
          name="hll_player_id"
          onChange={handleInputChange}
          type={"search"}
          placeholder={"Enter player ID"}
        />
        {!disableAddBtn && (
          <Tooltip title="Create">
            <span>
              <IconButton
                color="primary"
                onClick={() =>
                  handlePlayerSelect({
                    player_id: idInputValue,
                    name: nameInputValue,
                  })
                }
                disabled={!nameInputValue || !idInputValue}
              >
                <AddCircleOutline />
              </IconButton>
            </span>
          </Tooltip>
        )}
        <Popper
          open={isOpen && suggestions.length > 0}
          anchorEl={anchorEl}
          placement="bottom-start"
          style={{ width: anchorEl?.offsetWidth, zIndex: 1300 }}
        >
          <SuggestionsList elevation={3}>
            {suggestions.map((suggestion) => (
              <SuggestionItem
                key={suggestion.player_id}
                onClick={() => handlePlayerSelect(suggestion)}
              >
                <Avatar
                  variant="square"
                  src={suggestion.steaminfo?.profile?.avatarfull}
                >
                  {suggestion.names[0]?.name[0].toUpperCase()}
                </Avatar>
                <Typography sx={{ marginLeft: 1 }}>
                  {suggestion.names[0]?.name}
                </Typography>
              </SuggestionItem>
            ))}
          </SuggestionsList>
        </Popper>
      </Stack>
    </ClickAwayListener>
  );
}
