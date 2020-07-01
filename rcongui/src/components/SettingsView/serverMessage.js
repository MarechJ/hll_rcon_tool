import React from "react";
import {
  Grid, TextField, Button, jssPreset
} from "@material-ui/core";
import Autocomplete from '@material-ui/lab/Autocomplete';
import SplitButton from '../splitButton'
import TextHistory from '../textHistory'


const ServerMessage = ({ classes, type, value, setValue, onSave }) => {
  const textHistory = new TextHistory(type)

  return <Grid container xs={12}>
    <Grid item xs={12} className={classes.paddingBottom}>
    <Autocomplete
        freeSolo
        options={textHistory.getTexts()}
        inputValue={value}
        onInputChange={(e, value) => setValue(value)}
        renderInput={(params) => (
          <TextField multiline rows="4" {...params} label={type} margin="normal" variant="outlined" helperText={`Due to HLL limitations we can't know the current ${type}`} />
        )}
      />
    </Grid>
    <Grid item xs={12}>
      <SplitButton options={[`Set ${type}`, `Set ${type} and save as template`, "Save as template"]} clickHandlers={[() => onSave(value), () => { textHistory.saveText(value); onSave(value)}, () => textHistory.saveText(value)]} buttonProps={{variant: "outlined"}} />
    </Grid>
  </Grid>
}

export default ServerMessage