import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import {
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
} from "@mui/material";
import { MapDetailsCardCompact } from "./MapDetailsCard";

export function MapChangeDialog({
  mapLayer,
  open,
  onClose,
  onConfirm,
  pending = false,
  serverName,
}) {
  return (
    <Dialog
      open={open}
      onClose={pending ? undefined : onClose}
      fullWidth
      maxWidth="xs"
      aria-labelledby="map-change-dialog-title"
      aria-describedby="map-change-dialog-description"
    >
      <DialogTitle id="map-change-dialog-title">
        <div>Set current map: {mapLayer?.pretty_name}</div>
        <div>Server: {serverName || "this server"}</div>
      </DialogTitle>
      <DialogContent>
        <DialogContentText id="map-change-dialog-description">
          This will set a 60 seconds timer and override the current active map.
        </DialogContentText>
        {mapLayer && (
          <Box
            sx={{
              mt: 2,
              display: "flex",
              alignItems: "center",
              gap: 2,
              p: 2,
              borderRadius: 1,
              border: "1px solid",
              borderColor: "divider",
            }}
          >
            <MapDetailsCardCompact mapLayer={mapLayer} />
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="inherit" disabled={pending}>
          Cancel
        </Button>
        <Button
          onClick={onConfirm}
          color="primary"
          variant="contained"
          disabled={!mapLayer || pending}
          startIcon={
            pending ? (
              <CircularProgress size={20} color="inherit" />
            ) : (
              <CheckCircleIcon />
            )
          }
        >
          Confirm
        </Button>
      </DialogActions>
    </Dialog>
  );
}
