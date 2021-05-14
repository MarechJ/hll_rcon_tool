import React from "react";
import {Grid, TextField} from "@material-ui/core";
import Autocomplete from '@material-ui/lab/Autocomplete';
import SplitButton from '../splitButton'
import TextHistory from '../textHistory'
import {getSharedMessages} from "../../utils/fetchUtils";
import {ForwardCheckBox} from '../commonComponent'


const ServerMessage = ({ classes, type, autocompleteKey, value, setValue, onSave, forward, onForwardChange }) => {
  const textHistory = new TextHistory(autocompleteKey)
  const [sharedMessages, setSharedMessages] = React.useState([])
  React.useEffect(() => { getSharedMessages(autocompleteKey).then(data => setSharedMessages(data))  }, [autocompleteKey]);

  return <Grid container xs={12} alignItems="center" alignContent="center" justify="center">
    <Grid item xs={12} className={classes.paddingBottom}>
    <Autocomplete
        freeSolo
        options={sharedMessages.concat(textHistory.getTexts())}
        inputValue={value}
        onInputChange={(e, value) => setValue(value)}
        renderInput={(params) => (
          <TextField multiline rows={4} rowsMax={40} {...params} label={type} margin="normal" variant="outlined" 
          helperText={`Due to HLL limitations we can't know the current ${type}, what you see here is the best guess based on the last message set. Supports same variables as for auto broadcasts.`} />
        )}
      />
    </Grid>
    <Grid item>
      <ForwardCheckBox bool={forward} onChange={onForwardChange} />
    </Grid>
    <Grid item>
      <SplitButton options={[`Set ${type}`, `Set ${type} and save as template`, "Save as template"]} clickHandlers={[() => onSave(value), () => { textHistory.saveText(value, sharedMessages); onSave(value)}, () => textHistory.saveText(value, sharedMessages)]} buttonProps={{variant: "outlined"}} />
    </Grid>
  </Grid>
}

export default ServerMessage
