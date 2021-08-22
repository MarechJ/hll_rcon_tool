import React from "react";
import {
  Button,
  Grid,
  TextField,
  Typography
} from "@material-ui/core";
import { ForwardCheckBox } from "../commonComponent";


const AutoSettings = ({
  words,
  onWordsChange,
  onSave,
  forward,
  onFowardChange,
}) => (
  <Grid container>
    <Grid xs={12}>
      <TextField
        fullWidth
        label="Current auto settings"
        multiline
        rowsMax={32}
        rows={4}
        value={words}
        onChange={onWordsChange}
        placeholder="Wait! Where did all the code go? :("
        variant="outlined"
      />
    </Grid>
    <Typography variant="caption" align="left" color="textSecondary">
      For more info on how to use Auto Settings see <a href="https://youtu.be/2IKZwHj9PJw">this video</a>
    </Typography>
    <Grid xs={12}>
      <ForwardCheckBox bool={forward} onChange={onFowardChange} />
      <Button variant="outlined" color="secondary" onClick={onSave}>
        Save
      </Button>
    </Grid>
  </Grid>
);

export default AutoSettings;