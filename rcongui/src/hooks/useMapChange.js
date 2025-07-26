import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useGlobalStore } from "@/stores/global-state";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
  Box,
} from "@mui/material";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import { toast } from "react-toastify";
import {
  mapsManagerMutationOptions,
  mapsManagerQueryKeys,
} from "@/pages/settings/maps/queries";
import { MapDetailsCardCompact } from "@/pages/settings/maps/MapDetailsCard";

export const useMapChange = () => {
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [mapToConfirm, setMapToConfirm] = useState(null);
  const serverState = useGlobalStore((state) => state.serverState);
  const queryClient = useQueryClient();

  const { mutate: changeMap } = useMutation({
    ...mapsManagerMutationOptions.changeMap,
    onSuccess: (response) => {
      const mapName = response.arguments.map_name;
      queryClient.invalidateQueries({
        queryKey: mapsManagerQueryKeys.gameState,
      });
      toast.success(`Map has been changed to ${mapName}`, {
        toastId: `map-change-success`,
      });
    },
    onError: (error) => {
      toast.error(
        <div>
          <span>{error.name}</span>
          <p>{error.message}</p>
        </div>,
        {
          toastId: "map-change-error",
        }
      );
    },
  });

  const openMapChangeDialog = (mapLayer, mapOrdinal = 1) => {
    setMapToConfirm({ mapLayer, mapOrdinal });
    setConfirmDialogOpen(true);
  };

  const handleConfirmMapChange = () => {
    if (mapToConfirm) {
      setConfirmDialogOpen(false);
      changeMap({
        mapId: mapToConfirm.mapLayer.id,
        mapOrdinal: mapToConfirm.mapOrdinal,
      });
    }
  };

  const MapChangeDialog = () => (
    <Dialog
      open={confirmDialogOpen}
      onClose={() => setConfirmDialogOpen(false)}
      fullWidth
      maxWidth="xs"
      aria-labelledby="alert-dialog-title"
      aria-describedby="alert-dialog-description"
    >
      <DialogTitle>
        <div>Set current map: {mapToConfirm?.mapLayer?.pretty_name}</div>
        <div>Server: {serverState?.name || "this server"}</div>
      </DialogTitle>
      <DialogContent>
        <DialogContentText>
          This will set a 60 seconds timer and override the current active map.
        </DialogContentText>
        {mapToConfirm && (
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
            <MapDetailsCardCompact mapLayer={mapToConfirm.mapLayer} />
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setConfirmDialogOpen(false)} color="inherit">
          Cancel
        </Button>
        <Button
          onClick={handleConfirmMapChange}
          color="primary"
          variant="contained"
          startIcon={<CheckCircleIcon />}
        >
          Confirm
        </Button>
      </DialogActions>
    </Dialog>
  );

  return { MapChangeDialog, openMapChangeDialog };
};
