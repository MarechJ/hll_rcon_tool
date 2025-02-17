import React, { useEffect, useMemo, useRef, useState } from "react";
import { debounce } from "lodash";
import { handle_http_errors, postData, showResponse } from "@/utils/fetchUtils";
import Autocomplete from "@mui/material/Autocomplete";
import Typography from "@mui/material/Typography";
import { Avatar, Box } from "@mui/material";
import TextField from "@mui/material/TextField";

export default function PlayerAutocompletion({ player, setPlayer }) {
  const [suggestions, setSuggestions] = useState([]);

  const nameRef = useRef(player.name);

  useEffect(() => {
    debouncedFetchSuggestions();
    nameRef.current = player.name;
  }, [player.name]);

  const fetchSuggestions = () => {
    setSuggestions([]);

    if (!nameRef.current) {
      return;
    }

    const params = {
      page_size: 15,
      page: 1,
      player_name: nameRef.current,
      exact_name_match: false,
      ignore_accent: true,
    };
    postData(`${process.env.REACT_APP_API_URL}get_players_history`, params)
      .then((response) => showResponse(response, "get_players_history"))
      .then((data) => {
        if (data.failed) {
          return;
        }
        setSuggestions(data.result.players);
      })
      .catch(handle_http_errors);
  };

  const debouncedFetchSuggestions = useMemo(
    () => debounce(fetchSuggestions, 300),
    []
  );

  return (
    <Autocomplete
      freeSolo
      autoHighlight
      fullWidth
      options={suggestions}
      filterOptions={(options) => options}
      onChange={(_, value) => {
        setPlayer((prev) => ({
          ...prev,
          ...value,
          name: value?.names[0]?.name ?? "",
          player_id: value?.player_id ?? prev.player_id,
        }));
      }}
      getOptionLabel={(option) => option.names[0]?.name}
      renderOption={({ key, ...props }, option) => {
        return (
          <Box key={key} {...props}>
            <Avatar
              variant="square"
              src={option.steaminfo?.profile?.avatarfull}
            >
              {option.names[0]?.name[0].toUpperCase()}
            </Avatar>
            <Typography sx={{ marginLeft: 1 }}>
              {option.names[0]?.name}
            </Typography>
          </Box>
        );
      }}
      inputValue={player.name}
      onInputChange={(_, value) =>
        setPlayer((prev) => ({ ...prev, name: value }))
      }
      renderInput={(params) => (
        <TextField {...params} value={player.name} label={"Name"} type="text" />
      )}
    />
  );
}
