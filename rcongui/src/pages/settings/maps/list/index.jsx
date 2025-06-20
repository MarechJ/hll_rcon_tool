import { useOutletContext } from "react-router-dom";
import { useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
  Box,
  Typography,
} from "@mui/material";
import { MapList } from "../MapList";
import { MapChangeListItem } from "../rotation/MapListItem";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import { MapDetailsCard } from "../MapDetailsCard";
import { useGlobalStore } from "@/stores/global-state";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { mapsManagerMutationOptions, mapsManagerQueryKeys } from "../queries";
import { toast } from "react-toastify";
import { MapFilter } from "../MapFilter";

const MapListPage = () => {
  const { maps = [] } = useOutletContext();
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [mapToConfirm, setMapToConfirm] = useState(null);
  const [filteredMapOptions, setFilteredMapOptions] = useState(maps);
  const serverState = useGlobalStore((state) => state.serverState);
  const queryClient = useQueryClient()

  const { mutate: changeMap } = useMutation({
    ...mapsManagerMutationOptions.changeMap,
    onSuccess: (response) => {
      const mapName = response.arguments.map_name
      queryClient.invalidateQueries({
        queryKey: mapsManagerQueryKeys.gameState,
      });
      toast.success(`Map has been changed to ${mapName}`, {
        toastId: `map-change-success`,
      });
      setConfirmDialogOpen(false);
    },
    onError: () => {
      toast.error("Unable to change map", {
        toastId: "map-change-error",
      });
      setConfirmDialogOpen(false);
    },
  });

  const handleChangeMapClick = (mapLayer) => {
    setMapToConfirm(mapLayer);
    setConfirmDialogOpen(true);
  };

  const handleConfirmMapChange = () => {
    if (mapToConfirm) {
      changeMap(mapToConfirm.mapId || mapToConfirm.id);
    }
  };

  const handleFilterChange = (filteredMaps) => {
    setFilteredMapOptions(filteredMaps);
  };

  return (
    <>
      <Typography variant="h5" gutterBottom>
        Map List
      </Typography>
      <Typography variant="body2" gutterBottom color="textSecondary">
        Search for a map and click on it to set it as the current map.
      </Typography>
      <Box sx={{ height: "fit-content", zIndex: (theme) => theme.zIndex.appBar, pb: 2 }}>
        <MapFilter maps={maps} onFilterChange={handleFilterChange} />
      </Box>
      <MapList
        maps={filteredMapOptions}
        renderItem={(mapLayer) => (
          <MapChangeListItem
            mapLayer={mapLayer}
            key={mapLayer.id}
            onClick={handleChangeMapClick}
          />
        )}
      />
      {/* Confirmation Dialog */}
      <Dialog
        open={confirmDialogOpen}
        onClose={() => setConfirmDialogOpen(false)}
        fullWidth
        maxWidth="xs"
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle>
          Set current map to {mapToConfirm?.pretty_name} for{" "}
          {serverState?.name || "this server"}
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            This will set a 60 seconds timer and override the current active
            map.
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
              <MapDetailsCard mapLayer={mapToConfirm} />
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
    </>
  );
};

export default MapListPage;
