import * as React from "react";
import DraggableList from "./map-rotation-list";
import { reorder } from "../../../../components/MapManager/helpers";
import {
  changeMap,
  get,
  handle_http_errors,
  postData,
  showResponse,
} from "../../../../utils/fetchUtils";
import { Box, Button, CircularProgress } from "@mui/material";
import { Alert } from '@mui/material';
import { MapAutocomplete } from "../../../../components/MapManager/map-autocomplete";
import Grid from "@mui/material/Unstable_Grid2";

const Title = styled(Typography)(({ theme }) => ({
  marginTop: theme.spacing(2),
  marginBottom: theme.spacing(2),
  borderBottom: "1px solid",
  borderColor: theme.palette.divider,
}));

function MapRotationConfig() {

  return (
    <Grid container spacing={2}>
      <Grid xs={12}>
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
      <Grid xs={12}>
        <DraggableList
          maps={rotation}
          onDragEnd={onDragEnd}
          onRemove={onRemoveItem}
          onChange={onMapChange}
          isSaved={hasChanged}
        />
      </Grid>
    </Grid>
  );
};

export default MapRotation;
