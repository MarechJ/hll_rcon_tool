import React from "react";
import Autocomplete from '@mui/material/Autocomplete';
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import { DialogActions, DialogContent, DialogTitle } from "../dialog";
import FormHelperText from "@mui/material/FormHelperText";

// FIXME checkout https://mui.com/components/use-media-query/#migrating-from-withwidth
const withWidth = () => (WrappedComponent) => (props) => <WrappedComponent {...props} width="xs" />;

const Unban = ({
  bannedPlayers,
  width,
  handleUnban,
  onReload,
  onClose,
  open,
}) => {
  const [selectedPlayers, setSelectedPlayers] = React.useState([]);

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
        {bannedPlayers !== null ? (
          <Autocomplete
            multiple
            clearOnEscape
            id="tags-outlined"
            options={bannedPlayers}
            renderOption={(option) => `[${option.type}] ${option.raw}`}
            getOptionLabel={(option) => `${option.name} ${option.player_id}`}
            filterSelectedOptions
            onChange={(e, val) => setSelectedPlayers(val)}
            renderInput={(params) => (
              <TextField
                {...params}
                variant="outlined"
                label="Select players"
                fullWidth
              />
            )}
          />
        ) : (
          "Unable to show bans. Please retry"
        )}
        <FormHelperText >
          Don't forget to remove the Blacklisting as well for permabans
        </FormHelperText>
        <Button
          
          autoFocus
          onClick={onReload}
          variant="outlined"
          color="primary"
        >
          RELOAD LIST
        </Button>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="primary">
          Cancel
        </Button>
        <Button
          onClick={() => {
            selectedPlayers.map((p) => handleUnban(p));
            onClose();
          }}
          color="primary"
        >
          Confirm
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default withWidth()(Unban);
