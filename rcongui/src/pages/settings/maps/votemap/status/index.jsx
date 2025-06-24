import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  mapsManagerMutationOptions,
  mapsManagerQueryKeys,
  mapsManagerQueryOptions,
} from "../../queries";
import { MapList } from "../../MapList";
import { MapVotemapListItem } from "../../MapListItem";
import {
  Box,
  Button,
  CircularProgress,
  Divider,
  Stack,
  styled,
  Typography,
} from "@mui/material";
import PowerOffIcon from "@mui/icons-material/PowerOff";
import PowerIcon from "@mui/icons-material/Power";
import AutorenewIcon from "@mui/icons-material/Autorenew";
import { useLoaderData } from "react-router-dom";
import { toast } from "react-toastify";

const MapListContainer = styled(Box)(({ theme }) => ({
  width: "100%",
  [theme.breakpoints.up("md")]: {
    width: "50%",
  },
}));

const ActionsContainer = styled(Box)(({ theme }) => ({
  width: "100%",
  padding: theme.spacing(1),
  [theme.breakpoints.up("md")]: {
    width: "50%",
    borderLeft: `1px solid ${theme.palette.divider}`,
  },
}));

function VotemapStatusPage() {
  const loaderData = useLoaderData();
  const queryClient = useQueryClient();

  const { data: mapListStatus } = useQuery({
    ...mapsManagerQueryOptions.votemapStatus(),
    initialData: loaderData.mapListStatus,
    refetchInterval: 15_000,
    staleTime: 5_000,
    refetchOnMount: false,
  });

  const { data: config } = useQuery({
    ...mapsManagerQueryOptions.voteMapConfig(),
    initialData: loaderData.config,
    refetchInterval: 15_000,
    staleTime: 5_000,
    refetchOnMount: false,
  });

  const { mutate: toggleVotemap, isPending: isToggling } = useMutation({
    ...mapsManagerMutationOptions.setVotemapConfig,
    onSuccess: (response) => {
      const enabled = response.arguments.enabled;
      queryClient.invalidateQueries({
        queryKey: mapsManagerQueryKeys.voteMapConfig,
      });
      toast.success(`Votemap has been ${enabled ? "disabled" : "enabled"}.`);
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

  const { mutate: resetVotemap, isPending: isReseting } = useMutation({
    ...mapsManagerMutationOptions.resetVotemapState,
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: mapsManagerQueryKeys.votemapStatus,
      });
      toast.success(`Votemap has been reset.`);
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

  const handleVotemapToggle = () => {
    toggleVotemap({
      ...config,
      enabled: !config.enabled,
    });
  };

  return (
    <Stack direction={{ xs: "column-reverse", md: "row" }} spacing={1}>
      <MapListContainer>
        <MapList
          maps={mapListStatus.map((s) => s.map)}
          sort={false}
          renderItem={(mapLayer, index) => (
            <MapVotemapListItem
              key={mapLayer.id}
              mapLayer={mapLayer}
              voters={mapListStatus[index].voters}
            />
          )}
        />
      </MapListContainer>
      <ActionsContainer>
        <Typography variant="subtitle2" component={"div"}>
          Status: {config.enabled ? `🟢 ENABLED` : `🔴 DISABLED`}
        </Typography>
        <Typography variant="subtitle2" component={"div"}>
          Next map:{" "}
          {config.enabled
            ? mapListStatus[0]?.map?.pretty_name ?? "Unknown"
            : "N/A"}
        </Typography>
        <Divider orientation="horizontal" sx={{ my: 1 }} />
        <Stack direction="row" spacing={1} alignItems={"center"}>
          <Button
            onClick={handleVotemapToggle}
            startIcon={
              isToggling ? (
                <CircularProgress size={20} />
              ) : config.enabled ? (
                <PowerOffIcon />
              ) : (
                <PowerIcon />
              )
            }
            variant="contained"
            disabled={isToggling}
            color={config.enabled ? "error" : "success"}
            sx={{ minWidth: 120 }}
            size="small"
          >
            {config.enabled ? "Disable" : "Enable"}
          </Button>
          <Typography variant="caption">
            {config.enabled
              ? "votemap and decide the maps based on map rotation"
              : "votemap and decide maps dynamically on vote count or other conditions"}
          </Typography>
        </Stack>
        <Divider flexItem orientation="horizontal" sx={{ my: 1 }} />
        <Stack direction="row" spacing={1} alignItems={"center"}>
          <Button
            onClick={resetVotemap}
            disabled={isReseting}
            startIcon={
              isReseting ? <CircularProgress size={20} /> : <AutorenewIcon />
            }
            variant="contained"
            color="warning"
            sx={{ minWidth: 120 }}
            size="small"
          >
            Reset
          </Button>
          <Typography variant="caption">
            the current vote counts and generate new map pool
          </Typography>
        </Stack>
      </ActionsContainer>
    </Stack>
  );
}

export default VotemapStatusPage;
