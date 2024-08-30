import * as React from "react";
import {get, handle_http_errors, postData, showResponse,} from "../../../utils/fetchUtils";
import {Grid, Typography} from "@mui/material";
import Padlock from "../../shared/padlock";

const MapRotationSettings = () => {
  const [shuffleEnabled, setShuffleEnabled] = React.useState(false);

  const loadToState = (command, showSuccess, stateSetter) => {
    return get(command)
      .then((res) => showResponse(res, command, showSuccess))
      .then((res) => (res.failed === false ? stateSetter(res.result) : null))
      .catch(handle_http_errors);
  };

  const getShuffleEnabled = () => {
    loadToState("get_map_shuffle_enabled", false, setShuffleEnabled);
  };

  const toggleShuffleEnabled = (enabled) => {
    return postData(`${process.env.REACT_APP_API_URL}set_map_shuffle_enabled`, {
      enabled: enabled,
    })
      .then((res) => showResponse(res, `set_map_shuffle_enabled: ${enabled}`, true))
      .catch(handle_http_errors);
  };

  const loadAllData = () => {
    getShuffleEnabled();
  };

  React.useEffect(() => {
    loadAllData();
  }, []);

  return (
    (<Grid
      container
      spacing={2}
      justifyContent="flex-start"
      alignContent="center"
      alignItems="center"
    >
      <Grid item xs={12}>
        <Padlock
          label={<div style={{textAlign: 'start', display: 'flex', flexDirection: 'column'}}>
            <Typography variant={'body'}>Shuffle map rotation</Typography>
            <Typography variant={'caption'}>Will reset to default enabled when server restarts.</Typography>
          </div>}
          checked={shuffleEnabled}
          handleChange={(v) => {
            toggleShuffleEnabled(!shuffleEnabled);
            setShuffleEnabled(v);
          }}
        />
      </Grid>
    </Grid>)
  );
};

export default MapRotationSettings;
