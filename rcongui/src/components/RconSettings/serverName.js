import { Button, TextField } from "@mui/material";
import Grid from "@mui/material/Grid2";
import React from "react";
import {
  get,
  handle_http_errors,
  postData,
  showResponse,
} from "../../utils/fetchUtils";

const ServerName = () => {
  const [name, setName] = React.useState("");
  const isFirstRender = React.useRef(true);

  React.useEffect(() => {
    get("get_name")
      .then((res) => showResponse(res, "get_name", false))
      .then((res) => setName(res.result));
  }, []);

  const save = () => {
    postData(`${process.env.REACT_APP_API_URL}set_server_name`, {
      name: name,
    })
      .then((res) => showResponse(res, "set_server_name", true))
      .catch(handle_http_errors);
  };

  return (
    (<Grid container>
      <Grid size={10}>
        <TextField
          fullWidth
          lable="Server Name. ONLY FOR GTX USER (and if configured)"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
      </Grid>
      <Grid size={2}>
        <Button variant="outlined" onClick={save}>
          SAVE
        </Button>
      </Grid>
    </Grid>)
  );
};

export default ServerName;
