import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  mapsManagerMutationOptions,
  mapsManagerQueryKeys,
  mapsManagerQueryOptions,
} from "../../queries";
import Padlock from "@/components/shared/Padlock";
import { Typography } from "@mui/material";
import { toast } from "react-toastify";

function MapRotationSettings() {
  const queryClient = useQueryClient();
  const { data: shuffleEnabled } = useQuery({
    ...mapsManagerQueryOptions.mapRotationShuffle(),
    initialData: false,
  });
  const { mutate: setShuffleEnabled } = useMutation({
    ...mapsManagerMutationOptions.setMapRotationShuffle,
    onSuccess: (response) => {
      const enabled = response.arguments.enabled
      queryClient.invalidateQueries({
        queryKey: mapsManagerQueryKeys.mapRotationShuffle,
      });
      toast.success(`Map rotation shuffle is now ${enabled ? "enabled" : "disabled"}`);
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
    <Padlock
      label={
        <div
          style={{
            textAlign: "start",
            display: "flex",
            flexDirection: "column",
          }}
        >
          <Typography variant={"body"}>Shuffle map rotation</Typography>
          <Typography variant={"caption"}>
            This should randomly shuffle your map rotation.
          </Typography>
        </div>
      }
      name={"map-rotation-shuffle"}
      checked={shuffleEnabled}
      handleChange={setShuffleEnabled}
    />
  );
}

export default MapRotationSettings;
