import * as React from "react";
import {get, handle_http_errors, showResponse,} from "../../utils/fetchUtils";
import {Grid} from "@material-ui/core";
import Padlock from "../SettingsView/padlock";

const MapRotationSettings = ({classes}) => {
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

  const toggleShuffleEnabled = () => {
    return get("set_map_shuffle_enabled")
      .then((res) => showResponse(res, "set_map_shuffle_enabled", true))
      .catch(handle_http_errors);
  };

  const loadAllData = () => {
    getShuffleEnabled();
  };

  React.useEffect(() => {
    loadAllData();
  }, []);

  return (
    <Grid
      container
      spacing={2}
      justify="flex-start"
      alignContent="center"
      alignItems="center"
    >
      <Grid item xs={12}>
        <Padlock
          label="Shuffle map rotation"
          checked={shuffleEnabled}
          handleChange={(v) => {
            setShuffleEnabled(v);
            console.log(v);
            toggleShuffleEnabled();
          }}
        />
      </Grid>
    </Grid>
  );
};

export default MapRotationSettings;
