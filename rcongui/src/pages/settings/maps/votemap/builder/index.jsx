import { IconButton, LinearProgress, Tooltip } from "@mui/material";
import {
  mapsManagerMutationOptions,
  mapsManagerQueryKeys,
  mapsManagerQueryOptions,
} from "../../queries";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useLoaderData, useRouteLoaderData } from "react-router-dom";
import { toast } from "react-toastify";
import { useEffect, useMemo } from "react";
import { MapWhitelistList } from "../../MapList";
import { MapBuilderListItem } from "../../MapListItem";
import MapListBuilder from "../../MapListBuilder";
import RestoreIcon from "@mui/icons-material/Restore";

function VotemapBuilderPage() {
  const { maps } = useRouteLoaderData("maps");
  const loaderData = useLoaderData();
  const queryClient = useQueryClient();

  // Query to get current map rotation
  const { data: whitelist, isLoading: isLoadingWhitelist } = useQuery({
    ...mapsManagerQueryOptions.votemapWhitelist(),
    initialData: loaderData.whitelist,
    staleTime: 5_000,
    refetchOnMount: false,
  });

  const { mutate: saveWhitelist, isPending: isWhitelistSaving } = useMutation({
    ...mapsManagerMutationOptions.setWhitelist,
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: mapsManagerQueryKeys.votemapWhitelist,
      });
      toast.success("Votemap whitelist saved!");
    },
    onError: (error) => {
      toast.error(
        <div>
          <span>{error.name}</span>
          <p>{error.message}</p>
        </div>
      );
    },
  });

  const { mutate: resetWhitelist, isPending: isResetWhitelist } = useMutation({
    ...mapsManagerMutationOptions.resetVotemapWhitelist,
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: mapsManagerQueryKeys.votemapWhitelist,
      });
      toast.success("Votemap has been reset!");
    },
    onError: (error) => {
      toast.error(
        <div>
          <span>{error.name}</span>
          <p>{error.message}</p>
        </div>
      );
    },
  });

  const whitelistMaps = useMemo(
    () => whitelist.map((mapId) => maps.find((map) => map.id === mapId)),
    [whitelist]
  );

  const handleWhitelistSave = (mapIds) => {
    saveWhitelist(mapIds);
  };

  const checkForOutdatedMapIds = () => {
    if (whitelist) {
      const mapLayers = [];
      const invalidMapIds = [];
      whitelist.forEach((mapId) => {
        const mapLayer = maps.find((mapLayer) => mapLayer.id === mapId);
        if (mapLayer) {
          mapLayers.push(mapLayer);
        } else {
          invalidMapIds.push(mapId);
        }
      });
      if (invalidMapIds.length) {
        toast.error(
          `Some maps in your whitelist have been deleted or renamed: ${invalidMapIds.join(
            ", "
          )}. Reset the whitelist or changed your auto settings.`
        );
      }
    }
  };

  useEffect(checkForOutdatedMapIds, [whitelist]);

  return (
    <>
      {isLoadingWhitelist && (
        <LinearProgress
          sx={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            height: { xs: "3px", lg: "2px" },
          }}
        />
      )}
      <MapListBuilder
        maps={maps}
        selectedMaps={whitelistMaps}
        onSave={handleWhitelistSave}
        isSaving={isWhitelistSaving}
        isSaveDisabled={isWhitelistSaving}
        exclusive={true}
        slots={{
          SelectedMapList: MapWhitelistList,
          MapListItem: MapBuilderListItem,
        }}
        actions={
          <Tooltip title="Apply defaults - Reset whitelist to all available maps">
            <IconButton onClick={resetWhitelist} size="small" color="warning">
              <RestoreIcon />
            </IconButton>
          </Tooltip>
        }
      />
    </>
  );
}

export default VotemapBuilderPage;
