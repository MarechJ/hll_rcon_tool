import React from "react";
import {
  Grid, TextField, Button, jssPreset
} from "@material-ui/core";
import Autocomplete from '@material-ui/lab/Autocomplete';
import SplitButton from '../splitButton'
import TextHistory from '../textHistory'
import { getSharedMessages } from "../../utils/fetchUtils";

const ServerMessage = ({ classes, type, autocompleteKey, value, setValue, onSave }) => {
  const textHistory = new TextHistory(autocompleteKey)
  const [sharedMessages, setSharedMessages] = React.useState([])
  React.useEffect(() => { getSharedMessages(autocompleteKey).then(data => setSharedMessages(data))  }, []);

  return <Grid container xs={12}>
    <Grid item xs={12} className={classes.paddingBottom}>
    <Autocomplete
        freeSolo
        options={textHistory.getTexts().concat(sharedMessages)}
        inputValue={value}
        onInputChange={(e, value) => setValue(value)}
        renderInput={(params) => (
          <TextField multiline rows="4" {...params} label={type} margin="normal" variant="outlined" 
          helperText={`Due to HLL limitations we can't know the current ${type}. Supports same variables as for auto broadcasts.`} />
        )}
      />
    </Grid>
    <Grid item xs={12}>
      <SplitButton options={[`Set ${type}`, `Set ${type} and save as template`, "Save as template"]} clickHandlers={[() => onSave(value), () => { textHistory.saveText(value); onSave(value)}, () => textHistory.saveText(value)]} buttonProps={{variant: "outlined"}} />
    </Grid>
  </Grid>
}

export default ServerMessage
