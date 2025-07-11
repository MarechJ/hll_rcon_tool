import { useState, useEffect, useMemo } from "react";
import {
  Box,
  Grid2 as Grid,
  ToggleButtonGroup,
  ToggleButton,
  useMediaQuery,
  Badge,
} from "@mui/material";
import { MapFilter } from "./MapFilter";
import { MapList } from "./MapList";
import { styled, useTheme } from "@mui/material";
import _ from "lodash";

const MobileToggleGroup = styled(Grid)(({ theme }) => ({
  display: "block",
  marginTop: theme.spacing(1),
  [theme.breakpoints.up("md")]: {
    display: "none",
  },
}));

// As there might be duplicate map IDs in the list
// we need to assign a unique ID to each item
const withSelectionId = (mapLayer) => ({
  ...mapLayer,
  selectionId: `${mapLayer.id}-${Math.random().toString(36).slice(2, 9)}`,
});

/**
 * Map Selection Builder component for managing server map selection
 */
export function MapListBuilder({
  maps: allMaps = [],
  slots = {},
  selectedMaps = [],
  onSave,
  isSaveDisabled,
  isSaving,
  exclusive = false,
  actions,
}) {
  const [mapSelection, setMapSelection] = useState([]);
  const mapOptions = useMemo(() => {
    if (!exclusive) return allMaps;
    const selectedIds = new Set(mapSelection.map((m) => m.id));
    const exclusiveOptions = allMaps.filter((m) => !selectedIds.has(m.id));
    return exclusiveOptions;
  }, [exclusive, allMaps, mapSelection]);

  const [filteredMapOptions, setFilteredMapOptions] = useState(mapOptions);

  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down("md"));
  const [view, setView] = useState("map-list");
  const isMapListVisible =
    !isSmallScreen || (isSmallScreen && view === "map-list");
  const isMapSelectionVisible =
    !isSmallScreen || (isSmallScreen && view === "map-selection");

  // Set selection data when it's loaded
  useEffect(() => {
    if (selectedMaps.length > 0) {
      setMapSelection(selectedMaps.map(withSelectionId));
    }
  }, [selectedMaps]);

  const handleViewChange = (e, newView) => {
    if (newView === null) return; // force to keep one selected
    setView(newView);
  };

  // Add map to selection
  const addSelectionItem = exclusive
    ? _.debounce((mapLayer) => {
        const nextSelection = _.uniqBy(
          [...mapSelection, withSelectionId(mapLayer)],
          "id"
        );
        setMapSelection(nextSelection);
      }, 300)
    : _.throttle((mapLayer) => {
        const nextSelection = [...mapSelection, withSelectionId(mapLayer)];
        setMapSelection(nextSelection);
      }, 500);

  const handleFilterChange = (filteredMaps) => {
    setFilteredMapOptions(filteredMaps);
  };

  // Remove map from selection
  const removeSelectedItem = (mapItem) => {
    setMapSelection(
      mapSelection.filter((item) => item.selectionId !== mapItem.selectionId)
    );
  };

  // Clear selection
  const clearSelection = () => {
    setMapSelection([]);
  };

  // Handle save selection
  const handleSelectionSave = () => {
    onSave(mapSelection.map((item) => item.id));
  };

  // Reset selection to init value
  const handleSelectionReset = () => {
    setMapSelection(selectedMaps.map(withSelectionId));
  };

  return (
    <>
      <Grid container spacing={1}>
        <MobileToggleGroup size={12}>
          <ToggleButtonGroup
            fullWidth
            color="primary"
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

        {/* Left column - Map list */}
        {isMapListVisible && (
          <Grid size={{ xs: 12, md: 6 }}>
            <Box sx={{ mb: 3 }}>
              <Box
                sx={{
                  pb: 2,
                }}
              >
                <MapFilter
                  maps={mapOptions}
                  onFilterChange={handleFilterChange}
                />
              </Box>
              <Box
                sx={{
                  overflow: "auto",
                  scrollbarWidth: "thin",
                  position: "relative",
                  pr: 1,
                }}
              >
                <MapList
                  maps={filteredMapOptions}
                  emptyListMessage={"There are no more maps to add."}
                  renderItem={(mapLayer) => (
                    <slots.MapListItem
                      key={mapLayer.id}
                      mapLayer={mapLayer}
                      onClick={addSelectionItem}
                    />
                  )}
                />
              </Box>
            </Box>
          </Grid>
        )}

        {/* Right column - Map selection */}
        {isMapSelectionVisible && (
          <Grid
            size={{ xs: 12, md: 6 }}
            sx={{
              overflow: "auto",
              scrollbarWidth: "thin",
              position: "relative",
              pr: 1,
            }}
          >
            <slots.SelectedMapList
              maps={mapSelection}
              onRemove={removeSelectedItem}
              onClear={clearSelection}
              setMaps={setMapSelection}
              onReset={handleSelectionReset}
              // must come from parent element
              onSave={handleSelectionSave}
              isDisabled={isSaveDisabled}
              isSaving={isSaving}
              actions={actions}
            />
          </Grid>
        )}
      </Grid>
    </>
  );
}

export default MapListBuilder;
