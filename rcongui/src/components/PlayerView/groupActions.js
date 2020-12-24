import React from "react";
import Autocomplete from "@material-ui/lab/Autocomplete";
import TextField from "@material-ui/core/TextField";
import _ from "lodash";
import Button from "@material-ui/core/Button";
import Dialog from "@material-ui/core/Dialog";
import { PlayerActions, Duration } from "./playerActions";
import withWidth from "@material-ui/core/withWidth";
import { Reason } from "./textInputBar";
import Grid from "@material-ui/core/Grid";
import { DialogTitle, DialogContent, DialogActions } from "../dialog";
import { join } from 'lodash/array';
import TextHistory from '../textHistory'
import { fromJS, List } from 'immutable'
import { sortBy } from 'lodash/collection'
import { getSharedMessages } from "../../utils/fetchUtils";


const compactProfile = (player) => {
  let s = ""
  if (!player || !player.profile) {
    return s
  }
  s += ": "
  if (player.profile.flags) {
    s += join(player.profile.flags.map(f => f.flag), '')
  }

  return s
}

const GroupActions = ({
  players,
  classes,
  width,
  handleAction,
  onClose,
  open
}) => {
  const [message, setMessage] = React.useState("")
  const [selectedPlayers, setSelectedPlayers] = React.useState([])
  const [durationNumber, setDurationNumber] = React.useState(2)
  const [durationMultiplier, setDurationMultiplier] = React.useState(1)
  const [saveMessage, setSaveMessage] = React.useState(true)
  const textHistory = new TextHistory("punitions")
  const nbButton = ["xs"].indexOf(width) != -1 ? 3 : 6;
  const [sharedMessages, setSharedMessages] = React.useState([]);
  React.useEffect(() => {
    getSharedMessages("punitions").then((data) => setSharedMessages(data));
  }, []);

  let myPlayers = new List(players)
  myPlayers = myPlayers.toJS()

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
          autoFocus
          className={classes.marginBottom}
          multiple
          clearOnEscape
          id="tags-outlined"
          options={sortBy(myPlayers, p => p.name.toLowerCase())}
          getOptionLabel={option => `${option.name}${compactProfile(option)}`}
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
            <Reason
              message={message}
              handleMessageChange={setMessage}
              helperText={"A message is mandatory"}
              saveMessage={saveMessage}
              setSaveMessage={setSaveMessage}
              textHistory={textHistory}
            />
          </Grid>
          <Grid item xs={12} xl={12} className={classes.marginTop}>
            <PlayerActions
              handleAction={actionType =>
                selectedPlayers.map(p => {
                  if (saveMessage) {
                    textHistory.saveText(message, sharedMessages)
                  }
                  handleAction(actionType, p.name, message, durationNumber * durationMultiplier, p.steam_id_64)
                }
                )
              }
              message={message}
              disable={message === ""}
              displayCount={nbButton}
            />
          </Grid>
          <Grid item xs={12} xl={12} className={classes.marginTop}>
            <Duration durationNumber={durationNumber} onNumberChange={(number) => setDurationNumber(number)} durationMultiplier={durationMultiplier} onMultiplierChange={(multiplier) => setDurationMultiplier(multiplier)}/>
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="primary">
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default withWidth()(GroupActions);
