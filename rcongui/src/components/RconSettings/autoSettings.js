import React from "react";
import { Button } from "@mui/material";
import { ForwardCheckBox } from "../commonComponent";
import Editor from "@monaco-editor/react";
import Grid from "@mui/material/Unstable_Grid2";

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
    <Typography variant="caption" align="left">
      For more info on how to use Auto Settings see{" "}
      <a href="https://youtu.be/2IKZwHj9PJw" target="_blank">
        this video
      </a>{" "}
      or{" "}
      <a
        href="https://cdn.discordapp.com/attachments/729998051288285256/886276109484826634/autosettings_flow.PNG"
        target="_blank"
      >
        this flowchart
      </a>
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
