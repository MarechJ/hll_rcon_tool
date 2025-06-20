import { Box, Button, IconButton, Tooltip } from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import { MapDetailsCard } from "../MapDetailsCard";

function MapListItemBase({ mapLayer, renderActions }) {
  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        p: 0.5,
        mb: 1,
        borderRadius: 1,
        border: "1px solid",
        borderColor: "divider",
        "&:hover": { bgcolor: "action.hover" },
      }}
    >
      <MapDetailsCard mapLayer={mapLayer} />
      {renderActions && (
        <Box sx={{ display: "flex", gap: 1 }}>{renderActions(mapLayer)}</Box>
      )}
    </Box>
  );
}

export function MapListItem({ mapLayer }) {
  return <MapListItemBase mapLayer={mapLayer} />;
}

export function MapChangeListItem({ mapLayer, onClick }) {
  return (
    <MapListItemBase
      mapLayer={mapLayer}
      renderActions={(mapLayer) => (
        <Tooltip title="Set as current map">
          <span>
            <IconButton
              sx={{
                borderRadius: 0,
                bgcolor: "primary.main",
                color: "primary.contrastText",
                "&:hover": {
                  bgcolor: "primary.dark",
                },
              }}
              size="small"
              onClick={() => onClick(mapLayer)}
            >
              <PlayArrowIcon />
            </IconButton>
          </span>
        </Tooltip>
      )}
    />
  );
}

export function MapBuilderListItem({ mapLayer, onClick }) {
  return (
    <MapListItemBase
      mapLayer={mapLayer}
      renderActions={(mapLayer) => (
        <Button
          variant="contained"
          size="small"
          startIcon={<AddIcon />}
          onClick={() => onClick(mapLayer)}
        >
          Add
        </Button>
      )}
    />
  );
}
