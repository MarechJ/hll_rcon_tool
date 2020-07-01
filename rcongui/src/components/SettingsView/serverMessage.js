import React from "react";
import {
  Grid, TextField, Button, jssPreset
} from "@material-ui/core";
import Autocomplete from '@material-ui/lab/Autocomplete';
import SplitButton from '../splitButton'
import _ from 'lodash'

class TextHistory {
  constructor(namespace) {
    this.namespace = "autocomplete_" + namespace
  }

  getTexts() {
    let texts = localStorage.getItem(this.namespace)
    console.log("Loading history for ", this.namespace)
    if (!texts) {
      console.log("Loading history for ", this.namespace)
      texts = []
      localStorage.setItem(this.namespace, JSON.stringify(texts))
    } else {
      texts = JSON.parse(texts)
    }
    console.log(`History for ${this.namespace}: ${texts}`)
    return texts
  }

  saveText(text) {
    if (!text) {
      return
    }
    const texts = this.getTexts()
    texts.push(text)
    console.log(`Saving ${text} in ${this.namespace}`)
    localStorage.setItem(this.namespace, JSON.stringify(_.uniq(texts)))
  }

  clear() {
    localStorage.removeItem(this.namespace)
  }
}

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
      <SplitButton options={[`Set ${type}`, `Set ${type} and save as template`]} clickHandlers={[() => onSave(value), () => { textHistory.saveText(value); onSave(value)}]} buttonProps={{variant: "outlined"}} />
    </Grid>
  </Grid>
}

export default ServerMessage