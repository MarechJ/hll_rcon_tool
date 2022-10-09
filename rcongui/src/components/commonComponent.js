import React from "react";
import {
  Button,
  Checkbox,
  FormControlLabel,
  Grid,
  Popover,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Box,
  Typography,
  Slider,
  Input,
  Switch,
  FormGroup,
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

export function AlertDialog(props) {
  const [open, setOpen] = React.useState(false);
  const { buttonCaption, alertTitle, alertText, cancelText, onConfirmation, confirmText } = props

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    console.log("Canceled.")
    setOpen(false);
  };

  return (
    <div>
      <Button variant="outlined" onClick={handleClickOpen}>
        {buttonCaption}
      </Button>
      <Dialog
        open={open}
        onClose={handleClose}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">
          {alertTitle}
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            {alertText}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>{cancelText ?? "Cancel"}</Button>
          <Button onClick={() => {
            handleClose();
            onConfirmation();
          }} autoFocus>
            {confirmText ?? "Confirm"}
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}

export function InputSlider(props) {
  const { minValue, maxValue, label, defaultValue } = props

  const [value, setValue] = React.useState(30);

  const handleSliderChange = (event, newValue) => {
    setValue(newValue);
  };

  const handleInputChange = (event) => {
    setValue(event.target.value === '' ? '' : Number(event.target.value));
  };

  const handleBlur = () => {
    if (value < 0) {
      setValue(minValue || 0);
    } else if (value > maxValue) {
      setValue(maxValue);
    }
  };

  return (
    <Box sx={{ width: 250 }}>
      <Typography id="input-slider" gutterBottom>
        {label}
      </Typography>
      <Grid container spacing={2} alignItems="center">
        <Grid item xs>
          <Slider
            value={typeof value === 'number' ? value : 0}
            defaultValue={defaultValue}
            onChange={handleSliderChange}
            aria-labelledby="input-slider"
            steps={10}
            marks
            min={minValue}
            max={maxValue}
            size='large'
          />
        </Grid>
        <Grid item>
          <Input
            value={value}
            size="small"
            onChange={handleInputChange}
            onBlur={handleBlur}
            inputProps={{
              step: 10,
              min: minValue,
              max: maxValue,
              type: 'number',
              'aria-labelledby': 'input-slider',
            }}
          />
        </Grid>
      </Grid>
    </Box>
  );
}

export function Padlock({ handleChange, checked, label, color }) {

  return (
    <FormGroup row>
      <FormControlLabel
        control={
          <Switch
            checked={checked}
            onChange={e => handleChange(e.target.checked)}
            name={label}
            color={color ? color : "primary"}
          />
        }
        label={label}
      />
    </FormGroup>
  );
}