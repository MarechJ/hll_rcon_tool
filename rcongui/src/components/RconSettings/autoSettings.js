import React from "react";
import { Button, Grid, Typography } from "@material-ui/core";
import { ForwardCheckBox } from "../commonComponent";
import Editor from "@monaco-editor/react";

const AutoSettings = ({
  words,
  onWordsChange,
  onSave,
  forward,
  onFowardChange,
  onEditorMount,
}) => (
  <Grid container>
    <Grid xs={12}>
      <Editor
        height="90vh"
        defaultLanguage="json"
        defaultValue={words}
        onChange={onWordsChange}
        options={{
          minimap: { enabled: false },
          tabSize: 2,
        }}
        onMount={onEditorMount}
      />
    </Grid>
    <Grid xs={12}>
      <ForwardCheckBox bool={forward} onChange={onFowardChange} />
      <Button variant="outlined" color="secondary" onClick={onSave}>
        Save
      </Button>
    </Grid>
  </Grid>
);

export default AutoSettings;
