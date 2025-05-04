import { Typography, Box, LinearProgress } from "@mui/material";
import { useOutletContext } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { MapList } from "../MapList";
import { MapBuilderListItem } from "../rotation/MapListItem";
import MapListBuilder from "../MapListBuilder";
import { mapsManagerQueryOptions } from "../queries";
import { useMemo } from "react";
/**
 * Map Rotation page that contains the map rotation builder component
 */
function Votemap() {
  const { maps = [] } = useOutletContext();
  
  // Query to get current map rotation
  const { data: whitelistIds = [], isLoading: isLoadingWhitelist } = useQuery(mapsManagerQueryOptions.votemapWhitelist());

  const whitelist = useMemo(() => {
    return whitelistIds.map((id) => maps.find((map) => map.id === id));
  }, [whitelistIds, maps]);

  console.log(maps, whitelist);

  return (
    <>
      {isLoadingWhitelist && (
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
          selectedMaps={whitelist}
          slots={{
            SelectedMapList: MapList,
            MapListItem: MapBuilderListItem,
          }}
        />
      </Box>
    </>
  );
}

export default Votemap;
