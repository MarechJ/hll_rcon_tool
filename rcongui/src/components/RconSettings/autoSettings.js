import React from "react";
import {
  Button,
  Grid,
  TextField,
  Typography
} from "@material-ui/core";
import { ForwardCheckBox } from "../commonComponent";
import Editor from "@monaco-editor/react";


const AutoSettings = ({
  words,
  onWordsChange,
  onSave,
  forward,
  onFowardChange,
}) => (
  <Grid container>
    <Grid xs={12}>
      <Editor
        height="90vh"
        defaultLanguage="json"
        defaultValue={words}
        onChange={onWordsChange}
        options={{
          minimap: { enabled: false }
        }}
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