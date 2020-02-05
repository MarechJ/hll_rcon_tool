import React from "react";
import Autocomplete from "@material-ui/lab/Autocomplete";
import TextField from "@material-ui/core/TextField";
import _ from "lodash";
import { withStyles } from "@material-ui/core/styles";
import Button from "@material-ui/core/Button";
import Dialog from "@material-ui/core/Dialog";
import MuiDialogTitle from "@material-ui/core/DialogTitle";
import MuiDialogContent from "@material-ui/core/DialogContent";
import MuiDialogActions from "@material-ui/core/DialogActions";
import IconButton from "@material-ui/core/IconButton";
import CloseIcon from "@material-ui/icons/Close";
import Typography from "@material-ui/core/Typography";
import { PlayerActions } from "./playerActions";
import withWidth from "@material-ui/core/withWidth";
import { Reason } from "./textInputBar";
import Grid from "@material-ui/core/Grid";

const styles = theme => ({
  root: {
    margin: 0,
    padding: theme.spacing(2)
  },
  closeButton: {
    position: "absolute",
    right: theme.spacing(1),
    top: theme.spacing(1),
    color: theme.palette.grey[500]
  },
  marginBottom: {
    marginBottom: theme.spacing(1)
  }
});

const DialogTitle = withStyles(styles)(props => {
  const { children, classes, onClose, ...other } = props;
  return (
    <MuiDialogTitle disableTypography className={classes.root} {...other}>
      <Typography variant="h6">{children}</Typography>
      {onClose ? (
        <IconButton
          aria-label="close"
          className={classes.closeButton}
          onClick={onClose}
        >
          <CloseIcon />
        </IconButton>
      ) : null}
    </MuiDialogTitle>
  );
});

const test = (action, player, message) => (console.log(action, player, message))

const DialogContent = withStyles(theme => ({
  root: {
    padding: theme.spacing(2)
  }
}))(MuiDialogContent);

const DialogActions = withStyles(theme => ({
  root: {
    margin: 0,
    padding: theme.spacing(1)
  }
}))(MuiDialogActions);

const GroupActions = ({ players, classes, width, handleAction, onClose, open }) => {
  const [message, setMessage] = React.useState("");
  const [selectedPlayers, setSelectedPlayers] = React.useState([])

  const nbButton = width in ["sm", "xs"] ? 4 : 6;
  console.log(selectedPlayers)
  return (
    <Dialog
      onClose={onClose}
      aria-labelledby="customized-dialog-title"
      open={open}
      fullWidth={width}
      maxWidth={width}
    >
      <DialogTitle id="customized-dialog-title" onClose={onClose}>
        Apply same action on all selected players
      </DialogTitle>
      <DialogContent dividers>
        <Autocomplete
          className={classes.marginBottom}
          multiple
          id="tags-outlined"
          options={_.sortBy(players, p => p.name.toLowerCase())}
          getOptionLabel={option => option.name}
          filterSelectedOptions
          onChange={(e, val) => setSelectedPlayers(val)}
          renderInput={params => (
            <TextField
              {...params}
              variant="outlined"
              label="Select players"
              fullWidth
            />
          )}
        />
        <Grid container>
          <Grid item xs={12} xl={12} className={classes.marginBottom}>
            <Reason handleMessageChange={setMessage} helperText={"A message is mandatory"}/>
          </Grid>
          <Grid item xs={12} xl={12} className={classes.marginTop}>
            <PlayerActions handleAction={(actionType) => selectedPlayers.map((p) => handleAction(actionType, p.name, message))} disable={message === ""} displayCount={nbButton} />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button autoFocus onClick={onClose} color="primary">
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default withWidth()(GroupActions);
