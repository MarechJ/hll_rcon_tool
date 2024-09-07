import React, { useState, useEffect } from "react";
import { get, postData, showResponse } from "@/utils/fetchUtils";
import Editor from "@monaco-editor/react";
import { Button } from "@mui/material";
import Grid from "@mui/material/Grid2";
import { CopyBlock, dracula } from "react-code-blocks";
import { toast } from "react-toastify";

const UserSetting = ({
  description,
  getEndpoint,
  setEndpoint,
  validateEndpoint,
  describeEndpoint,
  notes,
  data,
  setEditorContent,
  refresh,
}) => {
  const [errors, setErrors] = useState([]);
  const [schema, setSchema] = useState("");

  useEffect(() => {
    get(describeEndpoint)
      .then((res) => showResponse(res, describeEndpoint, false))
      .then((res) => setSchema(JSON.stringify(res?.result, null, 2)));
  }, [describeEndpoint]);

  // const getData = (endpoint) => {
  //   setErrors([]);
  //   get(endpoint)
  //     .then((res) => showResponse(res, endpoint, true))
  //     .then((res) => setData(JSON.stringify(res?.result, null, 2)));
  // };

  const sendData = (endpoint) => {
    setErrors([]);
    try {
      postData(`${process.env.REACT_APP_API_URL}${endpoint}`, {
        ...JSON.parse(data),
        errors_as_json: true,
      })
        .then((res) => showResponse(res, endpoint, true))
        .then((res) => {
          if (res?.error) {
            setErrors([res.error]);
          }
        });
    } catch (error) {
      toast.error("Error parsing your settings JSON: " + error);
    }
  };

  return (<>
    <Grid container spacing={2}>
      <Grid size={12}>
        <h1>{description}</h1>
      </Grid>
      <Grid size={12}>
        <Button onClick={refresh}>Refresh</Button>
        <Button onClick={() => sendData(validateEndpoint)}>Validate</Button>
        <Button onClick={() => sendData(setEndpoint)}>Save</Button>
      </Grid>
      <Grid
        justifyContent="center"
        spacing={2}
        alignItems="center"
        direction="column"
        size={12}
      >
        <Editor
          height="70vh"
          defaultLanguage="json"
          onChange={setEditorContent}
          value={data}
          theme="vs-dark"
        />
      </Grid>
      <Grid size={12}>
        <h2>errors</h2>
        {errors.map((ele) => {
          return ele.type === "InvalidConfigurationError" ? (
            <div>
              <div>
                <b>Missing Keys</b>: {ele.missing_keys.join(", ")}
              </div>
              <div>
                <b>Mandatory Keys</b>: {ele.mandatory_keys.join(", ")}
              </div>
              <div>
                <b>Provided Keys</b>: {ele.provided_keys.join(", ")}
              </div>
            </div>
          ) : (
            <div>
              {Object.keys(ele).map((k) => {
                return (
                  <div>
                    <b>{k}</b>: {JSON.stringify(ele[k])}
                  </div>
                );
              })}
            </div>
          );
        })}
      </Grid>
      <Grid size={12}>
        {/* <Button onClick={() => getData(getEndpoint)}>Refresh</Button> */}
        <Button onClick={() => sendData(validateEndpoint)}>Validate</Button>
        <Button onClick={() => sendData(setEndpoint)}>Save</Button>
      </Grid>
    </Grid>
    <Grid size={12}>
      <h1>Documentation</h1>
      <div style={{ textAlign: "left" }}>
        <CopyBlock wrapLongLines text={notes} language="json" wrapLines theme={dracula} />
      </div>
    </Grid>
    <Grid size={12}>
      <h1>Model Schema</h1>
      <div style={{ textAlign: "left" }}>
        <CopyBlock wrapLongLines text={schema} language="json" wrapLines theme={dracula} />
      </div>
    </Grid>
  </>);
};

export default UserSetting;
