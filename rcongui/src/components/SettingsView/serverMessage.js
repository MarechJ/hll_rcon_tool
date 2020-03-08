import React from "react";
import {
  Grid, TextField, Button
} from "@material-ui/core";


const ServerMessage = ({ classes, type, value, setValue, onSave }) => (
    <Grid container xs={12}>
      <Grid item xs={12} className={classes.paddingBottom}>
        <TextField
          fullWidth
          label={type}
          multiline
          rows="4"
          variant="outlined"
          helperText={`Due to HLL limitations we can't know the current ${type}`}
          value={value}
          onChange={e => setValue(e.target.value)}
        />
      </Grid>
      <Grid item xs={12}>
        <Button fullWidth variant="outlined" onClick={() => onSave(value)}>Set {type}</Button>
      </Grid>
    </Grid>
  )

export default ServerMessage