import React, { Component } from "react";
import Grid from "@material-ui/core/Grid";
import TextField from "@material-ui/core/TextField";
import "react-toastify/dist/ReactToastify.css";
import ToggleButton from "@material-ui/lab/ToggleButton";
import ToggleButtonGroup from "@material-ui/lab/ToggleButtonGroup";
import SortByAlphaIcon from "@material-ui/icons/SortByAlpha";
import QueryBuilderIcon from "@material-ui/icons/QueryBuilder";
import TextHistory from '../textHistory'
import Autocomplete from '@material-ui/lab/Autocomplete';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Checkbox from '@material-ui/core/Checkbox';

const Reason = ({ handleMessageChange, extraClasses, helperText = "Leave blank if you want a confirmation popup", message, label = "Punish/Kick/Ban message", textHistory, saveMessage, setSaveMessage }) => {
  return < React.Fragment >
    <Autocomplete
      freeSolo
      fullWidth
      className={extraClasses}
      options={textHistory ? textHistory.getTexts() : []}
      inputValue={message}
      onInputChange={(e, value) => { if (e) { e.preventDefault()} ; handleMessageChange(value) }}
      renderInput={(params) => (
        <TextField {...params} label={label} margin="dense" helperText={helperText} />
      )}

    />
    {saveMessage !== undefined ?
      <FormControlLabel
        control={
          <Checkbox
            checked={saveMessage}
            onChange={() => setSaveMessage(!saveMessage)}
            color="primary"
          />
        }
        label="Save message as template"
      /> : ''}
  </React.Fragment >
}

const TextInputBar = ({
  classes,
  filter,
  handleChange,
  total,
  showCount,
  handleMessageChange,
  handleToggleAlphaSort
}) => {
  const [alignment, setAlignment] = React.useState("left");
  const handleToggle = (event, newAlignment) => {
    handleToggleAlphaSort(newAlignment === "centered");
    setAlignment(newAlignment);
  };

  /* todo refactor */
  return (
    <Grid item xs={12} spacing={2}>
      <Grid container justify="flex-start" direction="row" alignItems="center">
        <Grid item xs={12} md={1} className={classes.margin}>
          <ToggleButtonGroup
            value={alignment}
            exclusive
            size="small"
            onChange={handleToggle}
            aria-label="text alignment"
          >
            <ToggleButton value="centered">
              <SortByAlphaIcon />
            </ToggleButton>
          </ToggleButtonGroup>
        </Grid>
        <Grid item xs={12} md={3} className={classes.textLeft}>
          <TextField
            label="Filter"
            helperText={`Showing: ${showCount} / ${total}`}
            onChange={event => {
              event.preventDefault();
              handleChange(event.target.value);
            }}
          />
        </Grid>
        <Grid item xs={12} md={8} className={classes.textLeft}>
          <Reason handleMessageChange={handleMessageChange} />
        </Grid>
      </Grid>
    </Grid>
  );
};

export default TextInputBar;
export { TextInputBar, Reason }