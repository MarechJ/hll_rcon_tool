import React from "react";
import { Button } from "@mui/material";
import { ForwardCheckBox } from "../commonComponent";
import Editor from "@monaco-editor/react";
import Grid from "@mui/material/Grid2";

const AutoSettings = ({
  words,
  onWordsChange,
  onSave,
  forward,
  onFowardChange,
  onEditorMount,
}) => (
  <Grid container>
    <Grid size={12}>
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
    <Grid size={12}>
      <ForwardCheckBox bool={forward} onChange={onFowardChange} />
      <Button variant="outlined" color="secondary" onClick={onSave}>
        Save
      </Button>
    </Grid>
  </Grid>
);

export default AutoSettings;
