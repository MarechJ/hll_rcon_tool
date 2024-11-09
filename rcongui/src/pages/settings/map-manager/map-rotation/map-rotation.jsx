import * as React from "react";
import DraggableList from "./map-rotation-list";
import { reorder } from "@/components/MapManager/helpers";
import {
  changeMap,
  get,
  handle_http_errors,
  postData,
  showResponse,
} from "@/utils/fetchUtils";
import { Box, Button, CircularProgress } from "@mui/material";
import { Alert } from '@mui/material';
import { MapAutocomplete } from "@/components/MapManager/map-autocomplete";
import Grid from "@mui/material/Grid2";
import { useOutletContext } from "react-router-dom";

const MapRotation = () => {
  const { maps } = useOutletContext();
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

  const loadAllData = () => {
    getVoteMapConfig();
    loadMapRotation();
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

  const onRemoveItem = React.useCallback((index) => {
    rotation.splice(index, 1);
    setRotation(Array.from(rotation));
  });

  const onMapChange = React.useCallback((mapLayer) => {
    changeMap(mapLayer.id);
  });

  const hasChanged = React.useMemo(
    () =>
      currentRotation.map((o) => o.id).toString() ===
      rotation.map((o) => o.id).toString(),
    [currentRotation, rotation]
  );

  return (
    (<Grid container spacing={2}>
      <Grid size={12}>
        {voteMapConfig.enabled && (
          <Alert style={{ margin: "0.25rem 0 1rem 0" }} severity="warning">
            You can't change the rotation while votemap is on
          </Alert>
        )}
        <Box
          style={{
            display: "flex",
            justifyContent: "space-between",
            marginBottom: "1rem",
          }}
        >
          <Button size="small" variant="outlined" onClick={loadAllData}>
            Refresh
          </Button>
          <Box style={{ display: "flex", gap: "0.5rem" }}>
            <Button
              variant="outlined"
              disabled={hasChanged || rotationIsSaving || voteMapConfig.enabled}
              color={"secondary"}
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
        <Box style={{ display: "flex", gap: "0.5rem" }}>
          <MapAutocomplete
            options={maps}
            onChange={(e, v) => setMapsToAdd(v)}
            style={{ flexGrow: 1 }}
            disabled={voteMapConfig.enabled}
          />
          <Button
            size="small"
            variant="outlined"
            disabled={voteMapConfig.enabled}
            onClick={() => {
              setRotation(rotation.concat(mapsToAdd));
            }}
            style={{ width: 60 }}
          >
            Add
          </Button>
        </Box>
      </Grid>
      <Grid size={12}>
        <DraggableList
          maps={rotation}
          onDragEnd={onDragEnd}
          onRemove={onRemoveItem}
          onChange={onMapChange}
          isSaved={hasChanged}
        />
      </Grid>
    </Grid>)
  );
};

export default MapRotation;
