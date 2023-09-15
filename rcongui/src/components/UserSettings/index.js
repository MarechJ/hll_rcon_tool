import React, { useState, useEffect } from "react";
import { get, postData, showResponse } from "../../utils/fetchUtils";
import Editor from "@monaco-editor/react";
import { Button } from "@material-ui/core";
import { withRouter } from "react-router";
import Grid from "@material-ui/core/Grid";

const endpointToNames = new Map();
endpointToNames.set("get_audit_discord_webhooks_config", "Audit Webhooks");

const UserSetting = ({
  description,
  getEndpoint,
  setEndpoint,
  validateEndpoint,
}) => {
  const [data, setData] = useState("");
  const [errors, setErrors] = useState([]);

  useEffect(() => {
    getData(getEndpoint);
  }, [getEndpoint]);

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
          {/* <h1>{endpointToNames.get(getEndpoint)}</h1> */}
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
            width="75vw"
            height="75vh"
            defaultLanguage="json"
            value={data}
            onChange={setData}
            defaultValue={""}
          />
        </Grid>
        <Grid item xs={12}>
          <h2>errors</h2>
          {errors.map((ele) => {
            return (
              <div>
                {Object.keys(ele).map((k) => {
                  return (
                    <div>
                      <b>{k}</b>: {ele[k]}
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
      {/* 0// </> */}
    </>
  );
};

export default withRouter(UserSetting);
