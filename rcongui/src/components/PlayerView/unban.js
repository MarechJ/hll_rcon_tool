import React from "react";
import Autocomplete from "@material-ui/lab/Autocomplete";
import TextField from "@material-ui/core/TextField";
import _ from "lodash";
import Button from "@material-ui/core/Button";
import Dialog from "@material-ui/core/Dialog";
import {DialogTitle, DialogContent, DialogActions} from '../dialog'
import withWidth from "@material-ui/core/withWidth";
import moment from 'moment'
import FormHelperText from '@material-ui/core/FormHelperText';

const Unban = ({ bannedPlayers, classes, width, handleUnban, onReload, onClose, open }) => {
  const [message, setMessage] = React.useState("");
  const [selectedPlayers, setSelectedPlayers] = React.useState([])
 
  return (
    <Dialog
      onClose={onClose}
      aria-labelledby="customized-dialog-title"
      open={open}
      fullWidth={width}
      maxWidth={width}
    >
      <DialogTitle id="customized-dialog-title" onClose={onClose}>
        Unban players
      </DialogTitle>
      <DialogContent dividers>
        {bannedPlayers !== null ? 
        <Autocomplete
          className={classes.marginBottom}
          multiple
          clearOnEscape
          id="tags-outlined"
          options={bannedPlayers}
          renderOption={option => `${option.steam_id_64} ${option.name} [${option.type}] ${option.ban_time}`}
          getOptionLabel={option => `${option.name} ${option.steam_id_64}`}
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
        /> : 'Unable to show bans. Please retry'}
        <FormHelperText className={classes.paddingBottom}>Don't forget to remove the Blacklisting as well for permabans</FormHelperText>
        <Button className={classes.margin} autoFocus onClick={onReload} variant="outlined" color="primary">
          RELOAD LIST
        </Button>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="primary">
          Cancel
        </Button>
        <Button onClick={() => {selectedPlayers.map(p => handleUnban(p)); onClose()}} color="primary">
          Confirm
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default withWidth()(Unban);
