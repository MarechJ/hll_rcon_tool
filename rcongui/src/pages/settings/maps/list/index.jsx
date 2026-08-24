import { useRouteLoaderData } from "react-router-dom";
import { useState } from "react";
import { Box, Stack, styled, Typography } from "@mui/material";
import { MapList } from "../MapList";
import { MapChangeListItem } from "../MapListItem";
import { useGlobalStore } from "@/stores/global-state";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { mapsManagerMutationOptions, mapsManagerQueryKeys } from "../queries";
import { toast } from "react-toastify";
import { MapFilter } from "../MapFilter";
import RestartAltIcon from "@mui/icons-material/RestartAlt";
import { MapChangeDialog } from "../MapChangeDialog";

const MapListContainer = styled(Box)(({ theme }) => ({
  width: "100%",
  [theme.breakpoints.up("md")]: {
    width: "50%",
  },
}));

const ActionsContainer = styled(Box)(({ theme }) => ({
  width: "100%",
  paddingTop: theme.spacing(1),
  paddingBottom: theme.spacing(1),
  borderBottom: `1px solid ${theme.palette.divider}`,
  [theme.breakpoints.up("md")]: {
    padding: theme.spacing(1),
    width: "50%",
    borderLeft: `1px solid ${theme.palette.divider}`,
    borderBottom: "none",
  },
}));

const MapListPage = () => {
  const { maps } = useRouteLoaderData("maps");
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [mapToConfirm, setMapToConfirm] = useState(null);
  const [filteredMapOptions, setFilteredMapOptions] = useState(maps);
  const serverState = useGlobalStore((state) => state.serverState);
  const gameState = useGlobalStore((state) => state.gameState);
  const queryClient = useQueryClient();

  const { mutate: changeMap, isPending: isChangingMap } = useMutation({
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
      <Stack direction={{ xs: "column-reverse", md: "row" }} spacing={1}>
        <MapListContainer>
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
        </MapListContainer>
        <ActionsContainer>
          {gameState && (
            <>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                Current map
              </Typography>
              <MapChangeListItem
                mapLayer={gameState.current_map}
                key={gameState.current_map.id}
                onClick={handleChangeMapClick}
                icon={<RestartAltIcon />}
                title={"Restart the current map"}
              />
              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                Next map
              </Typography>
              <MapChangeListItem
                mapLayer={gameState.next_map}
                key={gameState.next_map.id}
                onClick={handleChangeMapClick}
              />
            </>
          )}
        </ActionsContainer>
      </Stack>
      <MapChangeDialog
        open={confirmDialogOpen}
        mapLayer={mapToConfirm}
        onClose={() => setConfirmDialogOpen(false)}
        onConfirm={handleConfirmMapChange}
        pending={isChangingMap}
        serverName={serverState?.name}
      />
    </>
  );
};

export default MapListPage;
