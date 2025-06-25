import { LinearProgress } from "@mui/material";
import MapListBuilder from "../../MapListBuilder";
import { cmd } from "@/utils/fetchUtils";
import {
  mapsManagerMutationOptions,
  mapsManagerQueryKeys,
} from "../../queries";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useLoaderData, useRouteLoaderData } from "react-router-dom";
import { toast } from "react-toastify";
import { SortableRotationList } from "./SortableRotationList";
import { MapBuilderListItem } from "../../MapListItem";

function MapRotationBuilder() {
  const { maps } = useRouteLoaderData("maps");
  const loaderData = useLoaderData()
  const queryClient = useQueryClient();

  // Query to get current map rotation
  const { data: currentRotation, isLoading: isLoadingRotation } = useQuery({
    queryKey: mapsManagerQueryKeys.mapRotation,
    queryFn: cmd.GET_MAP_ROTATION,
    initialData: loaderData.rotation,
    refetchOnMount: false,
  });

  const { mutate: saveRotation, isPending: isRotationSaving } = useMutation({
    ...mapsManagerMutationOptions.setMapRotation,
    onSuccess: (response) => {
      queryClient.invalidateQueries({
        queryKey: mapsManagerQueryKeys.mapRotation,
      });
      toast.success("Map rotation saved!");
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

  return (
    <>
      {isLoadingRotation && (
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
        selectedMaps={currentRotation}
        slots={{
          SelectedMapList: SortableRotationList,
          MapListItem: MapBuilderListItem,
        }}
        onSave={saveRotation}
        isSaving={isRotationSaving}
        isSaveDisabled={isRotationSaving}
      />
    </>
  );
}

export default MapRotationBuilder;
