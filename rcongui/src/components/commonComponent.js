import React from "react";
import { FormControlLabel, Checkbox } from "@material-ui/core";
import Chip from "@material-ui/core/Chip";
import Autocomplete from "@material-ui/lab/Autocomplete";
import TextField from "@material-ui/core/TextField";
import { Grid, Button, Tooltip } from "@material-ui/core";

export const ManualPlayerInput = ({
  name,
  setName,
  steam_id,
  setSteamId,
  reason,
  setReason,
  sharedMessages,
  textHistory,
  onSubmit,
  actionName,
  tooltipText,
  classes,
}) => (
  <Grid container spacing={1} justify="space-between">
    <Grid item xs={6} md={3}>
      <TextField
        id="steam-id"
        label="Steam ID"
        helperText="Required"
        value={steam_id}
        required
        fullWidth
        onChange={(e) => setSteamId(e.target.value)}
      />
    </Grid>
    <Grid item xs={6} md={3}>
      <TextField
        id="name"
        label="Player name"
        helperText="Optional"
        value={name}
        fullWidth
        onChange={(e) => setName(e.target.value)}
      />
    </Grid>
    <Grid item xs={12} md={4}>
      <Autocomplete
        freeSolo
        fullWidth
        options={sharedMessages.concat(textHistory.getTexts())}
        inputValue={reason}
        required
        onInputChange={(e, value) => setReason(value)}
        renderInput={(params) => (
          <TextField {...params} label="Reason" helperText="Required" />
        )}
      />
    </Grid>
    <Grid
      item
      xs={12}
      md={2}
      className={`${classes.padding} ${classes.margin}`}
    >
      <Tooltip fullWidth title={tooltipText} arrow>
        <Button
          color="secondary"
          variant="outlined"
          disabled={steam_id == "" || reason == ""}
          onClick={() => { onSubmit(); textHistory.saveText(reason); }}
        >
          {actionName}
        </Button>
      </Tooltip>
    </Grid>
  </Grid>
);

export const ForwardCheckBox = ({ bool, onChange }) => (
  <FormControlLabel
    control={
      <Checkbox
        checked={bool}
        onChange={(e) => {
          onChange(e.target.checked);
        }}
      />
    }
    label="Forward to all servers"
  />
);

export const WordList = ({
  words,
  onWordsChange,
  label,
  placeholder,
  helperText,
}) => {
  return (
    <Autocomplete
      multiple
      freeSolo
      options={[]}
      autoSelect
      onChange={(e, val) => onWordsChange(val)}
      value={words}
      renderTags={(value, getTagProps) =>
        value.map((option, index) => (
          <Chip
            color="primary"
            size="small"
            variant="outlined"
            label={option}
            {...getTagProps({ index })}
          />
        ))
      }
      renderInput={(params) => (
        <TextField
          {...params}
          label={label}
          placeholder={placeholder}
          helperText={helperText}
        />
      )}
    />
  );
};
