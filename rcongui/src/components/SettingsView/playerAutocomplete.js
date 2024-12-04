import React, {useEffect, useMemo, useRef} from "react";
import {handle_http_errors, postData, showResponse} from "../../utils/fetchUtils";
import Autocomplete from "@material-ui/lab/Autocomplete";
import Popper from "@material-ui/core/Popper";
import {Avatar, TextField, Typography} from "@material-ui/core";
import {debounce} from "lodash";

const PlayerAutocomplete = ({classes, name, setName, setPlayerId}) => {
  const [suggestions, setSuggestions] = React.useState([]);

  const nameRef = useRef(name);

  useEffect(() => {
    debouncedFetchSuggestions();
    nameRef.current = name;
  }, [name]);

  const fetchSuggestions = () => {
    setSuggestions([]);

    if (!nameRef.current) {
      return;
    }

    const params = {page_size: 15,
      page: 1,
      player_name: nameRef.current,
      exact_name_match: false,
      ignore_accent: true,
    };
    postData(
      `${process.env.REACT_APP_API_URL}get_players_history`,
      params
    )
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

  return <Autocomplete
    freeSolo
    autoHighlight
    fullWidth
    options={suggestions}
    filterOptions={(options) => options}
    onChange={(event, value, reason) => {
      if (reason === 'select-option') {
        setName(value.names[0]?.name);
        setPlayerId(value.player_id);
      }
    }}
    PopperComponent={(props) => (
      <Popper
        {...props}
        style={{
          minWidth: '400px',
          width: 'auto',
          maxWidth: '80vw',
        }}
      />
    )}
    getOptionLabel={(option) => option.names[0]?.name}
    renderOption={(option) => <>
      <Avatar
        variant="square"
        src={option.steaminfo?.profile?.avatarfull}
      >
        {option.names[0]?.name[0].toUpperCase()}
      </Avatar>
      <Typography className={classes.marginLeft}>{option.names[0]?.name}</Typography>
    </>
    }
    inputValue={name}
    onInputChange={(e, v) => setName(v)}
    renderInput={(params) =>
      <TextField
        {...params}
        value={name}
        label={"Name"}
        type="text"
        InputLabelProps={{
          shrink: true,
        }}
      />}
  />
};

export default PlayerAutocomplete;
