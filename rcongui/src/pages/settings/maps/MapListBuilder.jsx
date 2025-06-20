import { useState, useEffect } from "react";
import { Box, Typography, Alert, Grid2 as Grid } from "@mui/material";
import WarningIcon from "@mui/icons-material/Warning";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { handle_http_errors } from "@/utils/fetchUtils";
import { mapsManagerQueryKeys, mapsManagerMutationOptions } from "./queries";
import { MapFilter } from "./MapFilter";
import { MapList } from "./MapList";

/**
 * Map Rotation Builder component for managing server map rotation
 */
export function MapListBuilder({
  maps: allMaps = [],
  slots = {},
  selectedMaps = [],
}) {
  const queryClient = useQueryClient();
  const [mapSelection, setMapSelection] = useState([]);
  const [filteredMapOptions, setFilteredMapOptions] = useState(allMaps);

  // Set rotation data when it's loaded
  useEffect(() => {
    if (selectedMaps.length > 0) {
      setMapSelection(selectedMaps);
    }
  }, [selectedMaps]);

  // Query to get votemap configuration
  const { data: voteMapConfig = { enabled: false } } = useQuery({
    queryKey: mapsManagerQueryKeys.voteMapConfig,
    queryFn: async () => {
      const response = await fetch(
        `${process.env.REACT_APP_API_URL}get_votemap_config`
      );
      const data = await response.json();
      return data.result || { enabled: false };
    },
  });

  // Mutation to save map rotation
  const { mutate: saveRotation, isPending: isRotationSaving } = useMutation({
    ...mapsManagerMutationOptions.setMapRotation,
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: mapsManagerQueryKeys.mapRotation,
      });
    },
    onError: handle_http_errors,
  });

  // Add map to rotation
  const addToRotation = (mapLayer) => {
    // Create a copy of the variant with a unique rotationId
    const mapLayerWithUniqueId = {
      ...mapLayer,
      rotationId: `${mapLayer.id}-${Date.now()}-${Math.random()
        .toString(36)
        .substr(2, 9)}`,
    };

    setMapSelection([...mapSelection, mapLayerWithUniqueId]);
  };

  const handleFilterChange = (filteredMaps) => {
    setFilteredMapOptions(filteredMaps);
  };

  // Remove map from rotation
  const removeFromRotation = (rotationId) => {
    setMapSelection(
      mapSelection.filter((item) => (item.rotationId || item.id) !== rotationId)
    );
  };

  // Clear rotation
  const clearRotation = () => {
    setMapSelection([]);
  };

  // Handle save rotation
  const handleSaveRotation = () => {
    saveRotation(mapSelection.map((item) => item.mapId || item.id));
  };

  return (
    <Grid container spacing={3}>
      {/* Votemap warning alert */}
      {voteMapConfig.enabled && (
        <Grid size={12}>
          <Alert severity="warning" icon={<WarningIcon />} sx={{ mb: 2 }}>
            <Typography variant="body2">
              You can't change the rotation while votemap is on
            </Typography>
          </Alert>
        </Grid>
      )}

      {/* Left column - Map list */}
      <Grid size={{ xs: 12, md: 6 }}>
        <Box sx={{ mb: 3 }}>
          <Box
            sx={{
              height: "fit-content",
              zIndex: (theme) => theme.zIndex.appBar,
              pb: 2,
            }}
          >
            <MapFilter maps={allMaps} onFilterChange={handleFilterChange} />
          </Box>
          <Box
            sx={{
              maxHeight: { xs: "auto", lg: "calc(100vh - 25rem)" },
              overflow: "auto",
              scrollbarWidth: "thin",
              position: "relative",
              pr: 1,
            }}
          >
            <MapList
              maps={filteredMapOptions}
              renderItem={(mapLayer) => (
                <slots.MapListItem
                  key={mapLayer.id}
                  mapLayer={mapLayer}
                  onClick={addToRotation}
                />
              )}
            />
          </Box>
        </Box>
      </Grid>

      {/* Right column - Map rotation */}
      <Grid
        size={{ xs: 12, md: 6 }}
        sx={{
          maxHeight: { xs: "auto", lg: "calc(100vh - 20rem)" },
          overflow: "auto",
          scrollbarWidth: "thin",
          position: "relative",
          pr: 1,
        }}
      >
        <slots.SelectedMapList
          maps={mapSelection}
          onRemove={removeFromRotation}
          onSaveRotation={handleSaveRotation}
          onClearRotation={clearRotation}
          isSaveRotationDisabled={isRotationSaving || voteMapConfig.enabled}
          setMaps={setMapSelection}
          isRotationSaving={isRotationSaving}
        />
      </Grid>
    </Grid>
  );
}

export default MapListBuilder;
