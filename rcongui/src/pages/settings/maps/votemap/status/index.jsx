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
import AnnouncementIcon from '@mui/icons-material/Announcement';
import { useLoaderData } from "react-router-dom";
import { toast } from "react-toastify";
import dayjs from "dayjs";

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

  const { data: votemapStatus } = useQuery({
    ...mapsManagerQueryOptions.votemapStatus(),
    initialData: loaderData.votemapStatus,
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
      queryClient.invalidateQueries([
        mapsManagerQueryKeys.voteMapConfig,
        mapsManagerQueryKeys.votemapStatus,
      ]);
      toast.success(`Votemap has been ${enabled ? "enabled" : "disabled"}.`);
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

  const { mutate: sendReminder, isPending: isSendingReminder } = useMutation({
    ...mapsManagerMutationOptions.sendVotemapReminder,
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: mapsManagerQueryKeys.votemapStatus,
      });
      toast.success(`Votemap reminder has been sent.`);
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
          maps={votemapStatus.results.map((s) => s.map)}
          emptyListMessage={config.enabled ? "There are no maps in the selection. Your configuration may be too restrictive." : "Votemap is disabled."}
          sort={false}
          renderItem={(mapLayer, index) => (
            <MapVotemapListItem
              key={mapLayer.id}
              mapLayer={mapLayer}
              voters={votemapStatus.results[index].voters}
              votesCount={votemapStatus.results[index].votes_count}
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
            ? votemapStatus.next_map ?? "TBD"
            : "N/A"}
        </Typography>
        <Typography variant="subtitle2" component={"div"}>
          Last vote reminder:{" "}
          {votemapStatus.last_reminder ? dayjs(votemapStatus.last_reminder).fromNow() : "N/A"}
        </Typography>
        <Typography variant="subtitle2" component={"div"}>
          Next vote reminder:{" "}
          {votemapStatus.last_reminder ? dayjs(votemapStatus.last_reminder).add(config.reminder_frequency_minutes, "minutes").fromNow() : "N/A"}
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
            disabled={isReseting || !config.enabled}
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
        <Divider flexItem orientation="horizontal" sx={{ my: 1 }} />
        <Stack direction="row" spacing={1} alignItems={"center"}>
          <Button
            onClick={sendReminder}
            disabled={isSendingReminder || !config.enabled}
            startIcon={
              isSendingReminder ? <CircularProgress size={20} /> : <AnnouncementIcon />
            }
            variant="contained"
            sx={{ minWidth: 120 }}
            size="small"
          >
            Remind
          </Button>
          <Typography variant="caption">
            players to vote by sending all players in-game message.
          </Typography>
        </Stack>
      </ActionsContainer>
    </Stack>
  );
}

export default VotemapStatusPage;
