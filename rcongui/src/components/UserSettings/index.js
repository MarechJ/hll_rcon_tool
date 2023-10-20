import React, { useState, useEffect } from "react";
import { get, postData, showResponse } from "../../utils/fetchUtils";
import Editor from "@monaco-editor/react";
import { Button } from "@material-ui/core";
import { withRouter } from "react-router";
import Grid from "@material-ui/core/Grid";
import { CopyBlock, dracula } from "react-code-blocks";

const endpointToNames = new Map();
endpointToNames.set("get_audit_discord_webhooks_config", "Audit Webhooks");

const UserSetting = ({
  description,
  getEndpoint,
  setEndpoint,
  validateEndpoint,
  describeEndpoint,
  notes,
}) => {
  const [data, setData] = useState("");
  const [errors, setErrors] = useState([]);
  const [schema, setSchema] = useState("");

  useEffect(() => {
    getData(getEndpoint);
  }, [getEndpoint]);

  useEffect(() => {
    get(describeEndpoint)
      .then((res) => showResponse(res, describeEndpoint, false))
      .then((res) => setSchema(JSON.stringify(res?.result, null, 2)));
  }, [describeEndpoint]);

  const getData = (endpoint) => {
    setErrors([]);
    console.log(`fetching data from ${endpoint}`);
    get(endpoint)
      .then((res) => showResponse(res, endpoint, true))
      .then((res) => setData(JSON.stringify(res?.result, null, 2)));
  };

  const sendData = (endpoint) => {
    console.log(`sending data=${JSON.stringify(data)}`);
    setErrors([]);
    postData(`${process.env.REACT_APP_API_URL}${endpoint}`, {
      ...JSON.parse(data),
      errors_as_json: true,
    })
      .then((res) => showResponse(res, endpoint, true))
      .then((res) => {
        console.log(`post res=${JSON.stringify(res)}`);
        if (res?.error) {
          console.log(
            `error len=${JSON.parse(res.error).length} res.error=${res.error}`
          );
          setErrors(JSON.parse(res.error));
        }
      });
  };

  console.log(`errors=${JSON.stringify(errors)}`);

  return (
    <>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <h1>{description}</h1>
        </Grid>
        <Grid item xs={12}>
          <Button onClick={() => getData(getEndpoint)}>Refresh</Button>
          <Button onClick={() => sendData(validateEndpoint)}>Validate</Button>
          <Button onClick={() => sendData(setEndpoint)}>Save</Button>
        </Grid>
        <Grid
          item
          xs={12}
          justify="center"
          spacing={2}
          alignItems="center"
          justifyContent="center"
          direction="column"
        >
          <Editor
            width="90vw"
            height="50vh"
            defaultLanguage="json"
            value={data}
            onChange={setData}
            defaultValue={""}
            theme="vs-dark"
          />
        </Grid>
        <Grid item xs={12}>
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
        <Grid item xs={12}>
          <Button onClick={() => getData(getEndpoint)}>Refresh</Button>
          <Button onClick={() => sendData(validateEndpoint)}>Validate</Button>
          <Button onClick={() => sendData(setEndpoint)}>Save</Button>
        </Grid>
      </Grid>
      <Grid item xs={12}>
        <h1>Documentation</h1>
        <div style={{ textAlign: "left" }}>
          <CopyBlock text={notes} language="json" wrapLines theme={dracula} />
        </div>
      </Grid>
      <Grid item xs={12}>
        <h1>Model Schema</h1>
        <div style={{ textAlign: "left" }}>
          <CopyBlock text={schema} language="json" wrapLines theme={dracula} />
        </div>
      </Grid>
    </>
  );
};

export default withRouter(UserSetting);
