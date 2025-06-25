import {
  Box,
  Button,
  CircularProgress,
  Stack,
  Typography,
} from "@mui/material";
import { MapListItem, MapVotemapWhitelistItem } from "./MapListItem";
import CopyToClipboardButton from "@/components/shared/CopyToClipboardButton";
import SaveIcon from "@mui/icons-material/Save";
import DeleteIcon from "@mui/icons-material/Delete";
import ReplayIcon from "@mui/icons-material/Replay";

const EmptyMapList = () => {
  return (
    <Box
      sx={{
        py: 5,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        color: "text.secondary",
      }}
    >
      <Box sx={{ mb: 2, opacity: 0.5 }}>
        <svg width="48" height="48" viewBox="0 0 24 24">
          <path
            fill="currentColor"
            d="M12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22A10,10 0 0,1 2,12A10,10 0 0,1 12,2M12,12.5A1.5,1.5 0 0,1 10.5,11A1.5,1.5 0 0,1 12,9.5A1.5,1.5 0 0,1 13.5,11A1.5,1.5 0 0,1 12,12.5M12,7.2C9.9,7.2 8.2,8.9 8.2,11C8.2,14 12,17.5 12,17.5C12,17.5 15.8,14 15.8,11C15.8,8.9 14.1,7.2 12,7.2Z"
          />
        </svg>
      </Box>
      <Typography variant="h6" gutterBottom>
        No maps found
      </Typography>
      <Typography variant="body2">
        Try adjusting your filters or search term
      </Typography>
    </Box>
  );
};

/**
 * The maps are sorted alphabetically be default
 * @param {React.ReactNode} renderItem (optional) custom item component that accepts `mapLayer` as the only param
 * @returns
 */
export const MapList = ({ maps, renderItem, sort = true, ...props }) => {
  if (maps.length === 0) {
    return <EmptyMapList />;
  }

  return (
    <Box sx={{ overflow: "auto" }} {...props}>
      {(sort
        ? maps.sort((a, b) => a.map.name.localeCompare(b.map.name))
        : maps
      ).map((mapLayer, index, arr) =>
        renderItem ? (
          renderItem(mapLayer, index, arr)
        ) : (
          <MapListItem key={mapLayer.selectionId || mapLayer.id} mapLayer={mapLayer} />
        )
      )}
    </Box>
  );
};

export const MapWhitelistList = ({
  maps,
  setMaps,
  onReset,
  onRemove,
  onSave,
  onClear,
  isSaving,
  isDisabled,
}) => {
  return (
    <Box
      sx={{
        border: "1px solid",
        borderColor: "divider",
        borderRadius: 1,
        height: "100%",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <Box sx={{ p: 2, borderBottom: "1px solid", borderColor: "divider" }}>
        <Stack
          direction={{ xs: "column", sm: "row" }}
          gap={1}
          alignItems={"center"}
        >
          <Typography variant="h6">Whitelist ({maps.length})</Typography>
          <Box
            sx={{
              flexGrow: 1,
              display: "flex",
              justifyContent: "flex-end",
              gap: 1,
            }}
          >
            <Button
              variant="outlined"
              size={"small"}
              color="error"
              onClick={onReset}
              startIcon={<ReplayIcon />}
            >
              Reset
            </Button>
            <Button
              variant="outlined"
              size={"small"}
              color="error"
              onClick={onClear}
              startIcon={<DeleteIcon />}
            >
              Clear
            </Button>
            <CopyToClipboardButton
              title={
                <div>
                  <div>Copy the list of selected map ids to the clipboard.</div>
                  <div>Useful for autosettings.</div>
                </div>
              }
              text={JSON.stringify(
                maps.map((item) => item.mapId || item.id),
                null,
                2
              )}
              size={"small"}
            />
            <Button
              variant="contained"
              size={"small"}
              color="primary"
              disabled={isDisabled}
              onClick={onSave}
              startIcon={
                isSaving ? (
                  <CircularProgress size={20} color="inherit" />
                ) : (
                  <SaveIcon />
                )
              }
            >
              Save
            </Button>
          </Box>
        </Stack>
      </Box>
      <MapList
        maps={maps}
        renderItem={(mapLayer) => (
          <MapVotemapWhitelistItem
            key={mapLayer.selectionId || mapLayer.id}
            mapLayer={mapLayer}
            onClick={onRemove}
          />
        )}
        sx={{ p: 2 }}
      />
    </Box>
  );
};
