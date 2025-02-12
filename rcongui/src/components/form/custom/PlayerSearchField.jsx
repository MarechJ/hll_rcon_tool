import React, { useEffect, useMemo, useRef, useState } from "react";
import { debounce } from "lodash";
import { cmd, handle_http_errors, showResponse } from "@/utils/fetchUtils";
import Typography from "@mui/material/Typography";
import { 
  Avatar, 
  Box, 
  ClickAwayListener, 
  Paper, 
  Popper, 
  TextField,
  Tabs,
  Tab
} from "@mui/material";
import { styled } from "@mui/material/styles";

const SuggestionsList = styled(Paper)(({ theme }) => ({
  maxHeight: 300,
  overflow: 'auto',
  marginTop: theme.spacing(1),
}));

const SuggestionItem = styled(Box)(({ theme }) => ({
  padding: theme.spacing(1),
  display: 'flex',
  alignItems: 'center',
  cursor: 'pointer',
  '&:hover': {
    backgroundColor: theme.palette.action.hover,
  },
}));

export default function PlayerSearchField({ player, setPlayer }) {
  const [suggestions, setSuggestions] = useState([]);
  const [anchorEl, setAnchorEl] = useState(null);
  const [isOpen, setIsOpen] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const [searchMode, setSearchMode] = useState("name"); // "name" or "id"
  const inputRef = useRef(null);
  const nameRef = useRef(inputValue);

  useEffect(() => {
    debouncedFetchSuggestions();
    nameRef.current = inputValue;
  }, [inputValue]);

  const fetchSuggestions = async() => {
    setSuggestions([]);

    if (!nameRef.current) {
      setIsOpen(false);
      return;
    }

    const params = {
      payload: {
        page_size: 15,
        page: 1,
        [searchMode === "name" ? "player_name" : "player_id"]: nameRef.current,
        ignore_accent: true,
      }
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
    [searchMode] // Add searchMode as dependency
  );

  const handleInputChange = (event) => {
    const value = event.target.value;
    setInputValue(value);
    setAnchorEl(inputRef.current);
  };

  const handlePlayerSelect = (selectedPlayer) => {
    setPlayer((prev) => ({
      ...prev,
      ...selectedPlayer,
      name: selectedPlayer.names[0]?.name ?? "",
      player_id: selectedPlayer.player_id ?? prev.player_id,
    }));
    setInputValue("");
    setIsOpen(false);
  };

  const handleClickAway = () => {
    setIsOpen(false);
  };

  const handleTabChange = (_, newValue) => {
    setSearchMode(newValue);
    setInputValue("");
    setSuggestions([]);
    setIsOpen(false);
  };

  return (
    <ClickAwayListener onClickAway={handleClickAway}>
      <Box>
        <Tabs
          value={searchMode}
          onChange={handleTabChange}
          sx={{ mb: 2 }}
        >
          <Tab value="name" label="Search by Name" />
          <Tab value="id" label="Search by ID" />
        </Tabs>
        
        <TextField
          ref={inputRef}
          fullWidth
          label={searchMode === "name" ? "Name" : "Player ID"}
          value={inputValue}
          onChange={handleInputChange}
          type={"search"}
          placeholder={searchMode === "id" ? "Enter player ID" : "Enter player name"}
        />
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
      </Box>
    </ClickAwayListener>
  );
} 