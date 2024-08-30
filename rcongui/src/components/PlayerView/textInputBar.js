import React from "react";
import Grid from "@material-ui/core/Grid";
import TextField from "@material-ui/core/TextField";
import "react-toastify/dist/ReactToastify.css";
import TextHistory from "../textHistory";
import Autocomplete from "@material-ui/lab/Autocomplete";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import Checkbox from "@material-ui/core/Checkbox";

import InputLabel from "@material-ui/core/InputLabel";
import MenuItem from "@material-ui/core/MenuItem";
import FormHelperText from "@material-ui/core/FormHelperText";
import FormControl from "@material-ui/core/FormControl";
import Select from "@material-ui/core/Select";
import { getSharedMessages } from "../../utils/fetchUtils";

const Reason = ({
  handleMessageChange,
  helperText = "Leave blank if you want a confirmation popup",
  message,
  label = "In Game Message/Punish/Kick/Ban message",
  textHistory,
  saveMessage,
  setSaveMessage,
}) => {
  const autoCompletehistory = textHistory
    ? textHistory.getTexts()
    : new TextHistory("punishments").getTexts();

  const [sharedMessages, setSharedMessages] = React.useState([]);
  React.useEffect(() => {
    getSharedMessages("punishments").then((data) => setSharedMessages(data));
  }, []);

  return (
    <React.Fragment>
      <Autocomplete
        freeSolo
        fullWidth
        options={sharedMessages.concat(autoCompletehistory)}
        inputValue={message}
        onInputChange={(e, value) => {
          if (e) {
            e.preventDefault();
          }
          handleMessageChange(value);
        }}
        renderInput={(params) => (
          <TextField
            {...params}
            label={label}
            multiline
            rows={1}
            rowsMax={10}
            margin="dense"
            helperText={helperText}
          />
        )}
      />
      {saveMessage !== undefined ? (
        <FormControlLabel
          control={
            <Checkbox
              checked={saveMessage}
              onChange={() => setSaveMessage(!saveMessage)}
              color="primary"
            />
          }
          label="Save message as template"
        />
      ) : (
        ""
      )}
    </React.Fragment>
  );
};

const TextInputBar = ({
  handleChange,
  total,
  showCount,
  handleMessageChange,
  sortType,
  handleSortTypeChange,
}) => {
  /* todo refactor */
  return (
    <Grid item xs={12} spacing={2}>
      <Grid container justify="flex-start" direction="row" alignItems="center">
        <Grid item xs={12} lg={3}>
          <FormControl >
            <InputLabel>Sort</InputLabel>
            <Select
              value={sortType}
              onChange={(e) => handleSortTypeChange(e.target.value)}
            >
              <MenuItem value="">
                <em>None</em>
              </MenuItem>
              <MenuItem value={"asc_alpha"}>Asc. Alpha</MenuItem>
              <MenuItem value={"desc_alpha"}>Desc. Alpha</MenuItem>
              <MenuItem value={"asc_time"}>Asc. Time</MenuItem>
              <MenuItem value={"desc_time"}>Desc. Time</MenuItem>
              <MenuItem value={"asc_country"}>Asc. Country</MenuItem>
              <MenuItem value={"desc_country"}>Desc. Country</MenuItem>
              <MenuItem value={"asc_sessions"}>Asc. #Sessions</MenuItem>
              <MenuItem value={"desc_sessions"}>Desc. #Sessions</MenuItem>
              <MenuItem value={"asc_penalties"}>Asc. Penalties</MenuItem>
              <MenuItem value={"desc_penalties"}>Desc. Penalties</MenuItem>
              <MenuItem value={"asc_vips"}>Asc. VIPs</MenuItem>
              <MenuItem value={"desc_vips"}>Desc. VIPs</MenuItem>
            </Select>
            <FormHelperText>Sort the player list</FormHelperText>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={3} >
          <TextField
            label="Filter"
            helperText={`Showing: ${showCount} / ${total}`}
            onChange={(event) => {
              event.preventDefault();
              handleChange(event.target.value);
            }}
          />
        </Grid>
        <Grid item xs={12} lg={6} >
          <Reason handleMessageChange={handleMessageChange} />
        </Grid>
      </Grid>
    </Grid>
  );
};

export default TextInputBar;
export { TextInputBar, Reason };
