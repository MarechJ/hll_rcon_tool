import React from "react";
import {
  Button,
  Grid,
  TextField,
} from "@material-ui/core";
import {
  get,
  handle_http_errors,
  postData,
  showResponse,
} from "../../utils/fetchUtils";
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
        rowsMax={30}
        rows={4}
        value={words}
        onChange={onWordsChange}
        placeholder="For more info on how to use Auto Settings see https://placeholder.com"
        variant="outlined"
        helperText="For more info on how to use Auto Settings see https://placeholder.com"
      />
      <ForwardCheckBox bool={forward} onChange={onFowardChange} />
      <Button variant="outlined" color="secondary" onClick={onSave}>
        Save
      </Button>
    </Grid>
  </Grid>
);

export default AutoSettings;