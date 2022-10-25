import React from "react";
import {
  Button,
  Checkbox,
  FormControlLabel,
  Grid,
  Popover,
  Tooltip,
} from "@material-ui/core";
import Chip from "@material-ui/core/Chip";
import Autocomplete from "@material-ui/lab/Autocomplete";
import TextField from "@material-ui/core/TextField";

export const WithPopver = ({ classes, popoverContent, children }) => {
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handlePopoverOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handlePopoverClose = () => {
    setAnchorEl(null);
  };

  const open = Boolean(anchorEl);

  return (
    <React.Fragment>
      <div onMouseEnter={handlePopoverOpen} onMouseLeave={handlePopoverClose}>
        {children}
      </div>
      <Popover
        id="mouse-over-popover"
        className={classes.popover}
        classes={{
          paper: classes.paper,
        }}
        open={open}
        anchorEl={anchorEl}
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "left",
        }}
        transformOrigin={{
          vertical: "top",
          horizontal: "left",
        }}
        onClose={handlePopoverClose}
        disableRestoreFocus
      >
        {popoverContent}
      </Popover>
    </React.Fragment>
  );
};

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
          disabled={steam_id === "" || reason === ""}
          onClick={() => {
            onSubmit();
            textHistory.saveText(reason);
          }}
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

export const ExpiringVIPCheckBox = ({ bool, onChange }) => (
  <FormControlLabel
    control={
      <Checkbox
        checked={bool}
        onChange={(e) => {
          onChange(e.target.checked);
        }}
      />
    }
    label="Include Expiration Dates"
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
