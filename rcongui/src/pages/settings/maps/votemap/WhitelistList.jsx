import { Box, Typography, Button, CircularProgress } from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import SaveIcon from "@mui/icons-material/Save";
import CopyToClipboardButton from "@/components/shared/CopyToClipboardButton";
import { MapDetailsCard } from "../MapDetailsCard";
import { IconButton, Tooltip } from "@mui/material";
import { Box, Button, Typography, CircularProgress } from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import SaveIcon from "@mui/icons-material/Save";
import CopyToClipboardButton from "@/components/shared/CopyToClipboardButton";

export function WhitelistList({ whitelist }) {
  return (
    <Box
      sx={{
        border: "1px solid",
        borderColor: "divider",
        borderRadius: 1,
        bgcolor: "background.paper",
        height: "100%",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <Box sx={{ p: 2, borderBottom: "1px solid", borderColor: "divider" }}>
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            height: 50,
          }}
        >
          <Typography variant="h6">Map Rotation ({maps.length})</Typography>
          {maps.length > 0 && (
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
                color="error"
                onClick={onClearRotation}
                startIcon={<DeleteIcon />}
              >
                Clear
              </Button>
              <CopyToClipboardButton
                text={JSON.stringify(
                  maps.map((item) => item.mapId || item.id),
                  null,
                  2
                )}
              />
              <Button
                variant="contained"
                color="primary"
                disabled={isSaveRotationDisabled}
                onClick={onSaveRotation}
                startIcon={
                  isRotationSaving ? (
                    <CircularProgress size={20} color="inherit" />
                  ) : (
                    <SaveIcon />
                  )
                }
              >
                Save Rotation
              </Button>
            </Box>
          )}
        </Box>
      </Box>

      <Box sx={{ p: 2, flexGrow: 1, overflow: "auto" }}>
        {maps.length > 0 ? (
          maps.map((item) => (
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                p: 0.5,
                mb: 1,
                borderRadius: 1,
                bgcolor: "background.paper",
                border: "1px solid",
                borderColor: "divider",
                boxShadow: isDragging ? 3 : 1,
              }}
            >
              <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                <Box
                  {...attributes}
                  {...listeners}
                  sx={{
                    cursor: "grab",
                    "&:active": { cursor: "grabbing" },
                    p: 1,
                    borderRadius: 1,
                    "&:hover": { bgcolor: "action.hover" },
                  }}
                >
                  <svg width="24" height="24" viewBox="0 0 24 24">
                    <path
                      fill="currentColor"
                      d="M7,19V17H9V19H7M11,19V17H13V19H11M15,19V17H17V19H15M7,15V13H9V15H7M11,15V13H13V15H11M15,15V13H17V15H15M7,11V9H9V11H7M11,11V9H13V11H11M15,11V9H17V11H15M7,7V5H9V7H7M11,7V5H13V7H11M15,7V5H17V7H15Z"
                    />
                  </svg>
                </Box>
                <MapDetailsCard mapLayer={mapLayer} />
              </Box>
              <Box sx={{ display: "flex", gap: 1 }}>
                <Tooltip title="Remove from rotation">
                  <IconButton
                    size="small"
                    onClick={() => onRemove(item.rotationId || item.id)}
                    color="error"
                  >
                    <CloseIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            </Box>
          ))
        ) : (
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
              No maps in rotation
            </Typography>
            <Typography variant="body2">
              Add maps to build your rotation
            </Typography>
          </Box>
        )}
      </Box>
    </Box>
  );
}
