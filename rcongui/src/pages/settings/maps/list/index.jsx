import { useRouteLoaderData } from "react-router-dom";
import { useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
  Box,
} from "@mui/material";
import { MapList } from "../MapList";
import { MapChangeListItem } from "../MapListItem";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import { MapDetailsCardCompact } from "../MapDetailsCard";
import { useGlobalStore } from "@/stores/global-state";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { mapsManagerMutationOptions, mapsManagerQueryKeys } from "../queries";
import { toast } from "react-toastify";
import { MapFilter } from "../MapFilter";

const MapListPage = () => {
  const { maps } = useRouteLoaderData("maps");
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [mapToConfirm, setMapToConfirm] = useState(null);
  const [filteredMapOptions, setFilteredMapOptions] = useState(maps);
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
      setConfirmDialogOpen(false);
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
      <Box
        sx={{
          height: "fit-content",
          py: 2,
          maxWidth: theme => theme.breakpoints.values.md,
        }}
      >
        <MapFilter maps={maps} onFilterChange={handleFilterChange} />
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
      </Box>
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
          <div>Set current map: {mapToConfirm?.pretty_name}</div>
          <div>Server: {serverState?.name || "this server"}</div>
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
              <MapDetailsCardCompact mapLayer={mapToConfirm} />
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
