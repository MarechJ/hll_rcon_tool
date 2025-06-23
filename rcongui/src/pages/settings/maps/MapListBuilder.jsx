import { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Alert,
  Grid2 as Grid,
  ToggleButtonGroup,
  ToggleButton,
  useMediaQuery,
  Badge,
} from "@mui/material";
import WarningIcon from "@mui/icons-material/Warning";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { mapsManagerQueryKeys } from "./queries";
import { MapFilter } from "./MapFilter";
import { MapList } from "./MapList";
import { styled, useTheme } from "@mui/material";

const MobileToggleGroup = styled(Grid)(({ theme }) => ({
  display: "block",
  marginTop: theme.spacing(1),
  [theme.breakpoints.up("md")]: {
    display: "none",
  },
}));

/**
 * Map Rotation Builder component for managing server map rotation
 */
export function MapListBuilder({
  maps: allMaps = [],
  slots = {},
  selectedMaps = [],
  onSave,
  isSaveDisabled,
  isSaving,
}) {
  const queryClient = useQueryClient();
  const [mapSelection, setMapSelection] = useState([]);
  const [filteredMapOptions, setFilteredMapOptions] = useState(allMaps);
  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down("md"));
  const [view, setView] = useState("map-list");
  const isMapListVisible = !isSmallScreen || (isSmallScreen && view === "map-list")
  const isMapSelectionVisible = !isSmallScreen || (isSmallScreen && view === "map-selection")

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

  const handleViewChange = (e, newView) => {
    if (newView === null) return; // force to keep one selected
    setView(newView);
  };

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
    onSave(mapSelection.map((item) => item.mapId || item.id));
  };

  return (
    <>
      <Grid container spacing={1}>
        <MobileToggleGroup size={12}>
          <ToggleButtonGroup fullWidth color="primary"
            value={view}
            exclusive
            onChange={handleViewChange}
            aria-label="View"
          >
            <ToggleButton value="map-list">Map List</ToggleButton>
            <ToggleButton value="map-selection">
              Map Selection
              <Badge
                sx={{ pl: 2 }}
                showZero
                badgeContent={mapSelection.length}
                color="primary"
              ></Badge>
            </ToggleButton>
          </ToggleButtonGroup>
        </MobileToggleGroup>

        {/* Votemap warning alert */}
        {voteMapConfig.enabled && (
          <Grid size={12}>
            <Alert severity="warning" icon={<WarningIcon />}>
              <Typography variant="body2">
                You can't change the rotation while votemap is on
              </Typography>
            </Alert>
          </Grid>
        )}

        {/* Left column - Map list */}
        {isMapListVisible && (
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
        )}

        {/* Right column - Map rotation */}
        {isMapSelectionVisible && (
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
              onClearRotation={clearRotation}
              setMaps={setMapSelection}
              // must come from parent element
              onSaveRotation={handleSaveRotation}
              isSaveRotationDisabled={isSaveDisabled}
              isRotationSaving={isSaving}
            />
          </Grid>
        )}
      </Grid>
    </>
  );
}

export default MapListBuilder;
