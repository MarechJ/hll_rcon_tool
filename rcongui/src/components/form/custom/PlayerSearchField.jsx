import React, { useEffect, useRef, useState } from "react";
import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { cmd } from "@/utils/fetchUtils";
import Typography from "@mui/material/Typography";
import {
  Avatar,
  Box,
  Button,
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
  nameValue,
  onNameInputChange,
  idValue,
  onIdInputChange,
  disabled = false,
  required = false,
  allowIdOnlyAdd = false,
  addButtonFullWidth = false,
  ...props
}) {
  const [anchorEl, setAnchorEl] = useState(null);
  const [isOpen, setIsOpen] = useState(false);
  const [nameInputValue, setNameInputValue] = useState("");
  const [idInputValue, setIdInputValue] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState({ name: "", id: "" });
  const displayedNameValue = nameValue ?? nameInputValue;
  const displayedIdValue = idValue ?? idInputValue;

  const nameInputRef = useRef(null);
  const idInputRef = useRef(null);
  useEffect(() => {
    const timeout = window.setTimeout(() => {
      setDebouncedSearch({ name: displayedNameValue.trim(), id: displayedIdValue.trim() });
    }, 600);
    return () => window.clearTimeout(timeout);
  }, [displayedNameValue, displayedIdValue]);

  const { data: suggestions = [] } = useQuery({
    queryKey: ["players", "search", debouncedSearch],
    queryFn: async () => {
      const response = await cmd.GET_PLAYERS_RECORDS({
        payload: {
          page_size: 15,
          page: 1,
          player_name: debouncedSearch.name,
          player_id: debouncedSearch.id,
          ignore_accent: true,
        },
        throwRouteError: false,
      });
      return response?.result?.players ?? [];
    },
    enabled: !disabled && Boolean(debouncedSearch.name || debouncedSearch.id),
    placeholderData: keepPreviousData,
  });

  const handleInputChange = (event) => {
    const value = event.target.value;
    if (event.target.name === "hll_player_name") {
      setNameInputValue(value);
      onNameInputChange?.(value);
      setAnchorEl(nameInputRef.current);
    } else {
      setIdInputValue(value);
      onIdInputChange?.(value);
      setAnchorEl(idInputRef.current);
    }
    setIsOpen(Boolean(value));
  };

  const handlePlayerSelect = (selectedPlayer) => {
    onSelect(selectedPlayer);
    if (nameValue === undefined) setNameInputValue("");
    if (idValue === undefined) setIdInputValue("");
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
          value={displayedNameValue}
          name="hll_player_name"
          onChange={handleInputChange}
          type={"search"}
          placeholder={"Enter player name"}
          disabled={disabled}
          required={required}
        />
        <TextField
          ref={idInputRef}
          fullWidth
          label={"Player ID"}
          value={displayedIdValue}
          name="hll_player_id"
          onChange={handleInputChange}
          type={"search"}
          placeholder={"Enter player ID"}
          disabled={disabled}
          required={required}
        />
        {!disableAddBtn && !addButtonFullWidth && (
          <Tooltip title="Create">
            <span>
              <IconButton
                color="primary"
                onClick={() =>
                  handlePlayerSelect({
                    player_id: displayedIdValue,
                    name: displayedNameValue,
                  })
                }
                disabled={
                  disabled ||
                  !displayedIdValue ||
                  (!allowIdOnlyAdd && !displayedNameValue)
                }
              >
                <AddCircleOutline />
              </IconButton>
            </span>
          </Tooltip>
        )}
        {!disableAddBtn && addButtonFullWidth && (
          <Button
            type="button"
            variant="outlined"
            fullWidth
            startIcon={<AddCircleOutline />}
            onClick={() => handlePlayerSelect({
              player_id: displayedIdValue,
              name: displayedNameValue,
            })}
            disabled={
              disabled ||
              !displayedIdValue ||
              (!allowIdOnlyAdd && !displayedNameValue)
            }
          >
            Add player
          </Button>
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
