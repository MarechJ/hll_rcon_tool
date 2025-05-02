import { MapListBuilder } from "../MapListBuilder";
import { Typography, Box, Paper, LinearProgress } from "@mui/material";
import { useOutletContext } from "react-router-dom";
import { SortableRotationList } from "./SortableRotationList";
import { MapBuilderListItem } from "./MapListItem";
import { useQuery } from "@tanstack/react-query";
import { mapsManagerQueryKeys } from "../queries";
import { cmd } from "@/utils/fetchUtils";

/**
 * Map Rotation page that contains the map rotation builder component
 */
function MapRotation() {
  const { maps = [] } = useOutletContext();

  // Query to get current map rotation
  const { data: currentRotation, isLoading: isLoadingRotation } = useQuery({
    queryKey: mapsManagerQueryKeys.mapRotation,
    queryFn: cmd.GET_MAP_ROTATION,
  });

  return (
    <>
      {isLoadingRotation && (
        <LinearProgress
          sx={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            height: { xs: "3px", lg: "2px" },
          }}
        />
      )}
      <Typography variant="h5" gutterBottom>
        Map Rotation
      </Typography>
      <Typography variant="body2" gutterBottom color="textSecondary">
        Configure the map rotation for your server. Drag and drop maps to
        reorder them.
      </Typography>

      <Box sx={{ mt: 3 }}>
        <MapListBuilder
          maps={maps}
          selectedMaps={currentRotation}
          slots={{
            SelectedMapList: SortableRotationList,
            MapListItem: MapBuilderListItem,
          }}
        />
      </Box>
    </>
  );
}

export default MapRotation;
