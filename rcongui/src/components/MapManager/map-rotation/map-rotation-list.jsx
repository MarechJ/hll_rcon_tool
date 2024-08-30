import * as React from "react";
import DraggableList from "../DraggableList";
import { reorder } from "../helpers";
import {
  get,
  handle_http_errors,
  postData,
  showResponse,
} from "../../../utils/fetchUtils";
import { Box, Button, CircularProgress, Grid } from "@mui/material";
import Autocomplete from '@mui/material/Autocomplete';
import TextField from "@mui/material/TextField";
import { Alert } from '@mui/material';

const MapRotation = () => {
  const [maps, setMaps] = React.useState([]);
  const [currentRotation, setCurrentRotation] = React.useState([]);
  const [rotation, setRotation] = React.useState([]);
  const [mapsToAdd, setMapsToAdd] = React.useState([]);
  const [rotationIsSaving, setRotationIsSaving] = React.useState(false);
  const [voteMapConfig, setVoteMapConfig] = React.useState({});
  const [lastRefresh, setLastRefresh] = React.useState(null);

  const loadToState = (command, showSuccess, stateSetter) => {
    return get(command)
      .then((res) => showResponse(res, command, showSuccess))
      .then((res) => (res.failed === false ? stateSetter(res) : null))
      .catch(handle_http_errors);
  };

  const saveRotation = () => {
    setRotationIsSaving(true);
    return postData(`${process.env.REACT_APP_API_URL}set_maprotation`, {
      map_names: rotation.map((m) => m.id),
    })
      .then((res) => {
        showResponse(res, `set_maprotation`, true);
        setRotationIsSaving(false);
        loadMapRotation();
      })
      .catch((e) => {
        handle_http_errors(e);
        loadMapRotation();
        setRotationIsSaving(false);
      });
  };

  const getVoteMapConfig = () => {
    get("get_votemap_config")
      .then((res) => showResponse(res, "get_votemap_config", false))
      .then((data) => (data.failed ? "" : setVoteMapConfig(data.result)))
      .catch(handle_http_errors);
  };

  const loadMapRotation = () => {
    return loadToState("get_map_rotation", false, (data) => {
      setCurrentRotation(Array.from(data.result));
      setRotation(Array.from(data.result));
    });
  };

  const loadAllMaps = () => {
    return loadToState("get_maps", false, (data) => setMaps(data.result));
  };

  const loadAllData = () => {
    getVoteMapConfig();
    loadMapRotation();
    loadAllMaps();
    setLastRefresh(new Date());
  };

  React.useEffect(() => {
    loadAllData();
    const handle = setInterval(getVoteMapConfig, 10000);

    return () => clearInterval(handle);
  }, []);

  const onDragEnd = ({ destination, source }) => {
    // dropped outside the list
    if (!destination) return;

    const newRotation = reorder(rotation, source.index, destination.index);

    setRotation(newRotation);
  };

  const onRemoveItem = (index) => {
    rotation.splice(index, 1);
    setRotation(Array.from(rotation));
  };

  const hasChanged = React.useMemo(
    () => currentRotation.map((o) => o.id).toString() === rotation.map((o) => o.id).toString(),
    [currentRotation, rotation]
  );

  return (
    <Grid container spacing={2}>
      <Grid item xs={12}>
        {voteMapConfig.enabled && <Alert style={{ margin: "0.25rem 0 1rem 0" }} severity="warning" >You can't change the rotation while votemap is on</Alert>}
        <Box style={{ display: "flex", justifyContent: "space-between", marginBottom: "1rem" }}>
          <Button size="small" variant="outlined" onClick={loadAllData}>
            Refresh
          </Button>
          <Box style={{ display: "flex", gap: "0.5rem" }}>
            <Button
              size="small"
              variant="outlined"
              disabled={voteMapConfig.enabled}
              onClick={() => {
                setRotation(rotation.concat(mapsToAdd));
              }}
            >
              Add
            </Button>
            <Button
              variant="outlined"
              disabled={hasChanged || rotationIsSaving || voteMapConfig.enabled}
              onClick={saveRotation}
              size="small"
            >
              {rotationIsSaving ? (
                <CircularProgress size={20} />
              ) : (
                "Save rotation"
              )}
            </Button>
          </Box>
        </Box>
          <Autocomplete
            multiple
            disabled={voteMapConfig.enabled}
            size="small"
            disableCloseOnSelect
            options={maps}
            getOptionLabel={(m) => m.pretty_name}
            isOptionEqualToValue={(option, value) => option.id == value.id}
            onChange={(e, v) => setMapsToAdd(v)}
            renderInput={(params) => (
              <TextField
                {...params}
                variant="outlined"
                label="Select maps"
              />
            )}
          />
      </Grid>
      <Grid item xs={12}>
        <DraggableList
          items={rotation}
          onDragEnd={onDragEnd}
          onRemove={onRemoveItem}
        />
      </Grid>
    </Grid>
  );
};

export default MapRotation;
