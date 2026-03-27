import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  mapsManagerMutationOptions,
  mapsManagerQueryKeys,
  mapsManagerQueryOptions,
} from "../../queries";
import { MapList } from "../../MapList";
import {
  MapVotemapListItem,
  MapVotemapResultListItem,
} from "../../MapListItem";
import {
  Box,
  Button,
  CircularProgress,
  Divider,
  Pagination,
  Stack,
  styled,
  Typography,
} from "@mui/material";
import PowerOffIcon from "@mui/icons-material/PowerOff";
import PowerIcon from "@mui/icons-material/Power";
import AutorenewIcon from "@mui/icons-material/Autorenew";
import AnnouncementIcon from "@mui/icons-material/Announcement";
import AddIcon from "@mui/icons-material/Add";
import StarIcon from '@mui/icons-material/Star';
import { useLoaderData } from "react-router-dom";
import { toast } from "react-toastify";
import dayjs from "dayjs";
import { useState } from "react";
import MapAutocomplete from "@/components/shared/MapAutocomplete";

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

  const { data: maps } = useQuery({
    ...mapsManagerQueryOptions.maps(),
    initialData: [],
  });

  const { data: votemapStatus } = useQuery({
    ...mapsManagerQueryOptions.votemapStatus(),
    initialData: loaderData.votemapStatus,
    refetchInterval: 15_000,
    staleTime: 5_000,
    refetchOnMount: false,
  });

  const { data: votemapResults } = useQuery({
    ...mapsManagerQueryOptions.votemapResults(),
    initialData: loaderData.votemapResults,
    refetchInterval: 60_000,
    staleTime: 5_000,
    refetchOnMount: false,
  });

  const [resultHistoryPage, setResultHistoryPage] = useState(1);
  const handleResultHistoryPageChange = (event, value) => {
    setResultHistoryPage(value);
  };
  const [selectedMap, setSelectedMap] = useState(null);

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

  const { mutate: removeMapFromVotemap } = useMutation({
    ...mapsManagerMutationOptions.removeMapFromVotemap,
    onSuccess: (response) => {
      const mapName = response.arguments.map_name;
      queryClient.invalidateQueries({
        queryKey: mapsManagerQueryKeys.votemapStatus,
      });
      toast.success(
        `Map ${mapName} was successfully removed from the current selection.`
      );
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

  const { mutate: addMapToVotemap, isPending: isAddingMapToVotemap } =
    useMutation({
      ...mapsManagerMutationOptions.addMapToVotemap,
      onSuccess: (response) => {
        const mapName = response.arguments.map_name;
        queryClient.invalidateQueries({
          queryKey: mapsManagerQueryKeys.votemapStatus,
        });
        toast.success(
          `Map ${mapName} was successfully added to the current selection.`
        );
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

    const { mutate: setVotemapWinner, isPending: isSettingVotemapWinner } =
    useMutation({
      ...mapsManagerMutationOptions.setVotemapWinner,
      onSuccess: (response) => {
        const mapName = response.arguments.map_name;
        queryClient.invalidateQueries({
          queryKey: mapsManagerQueryKeys.votemapStatus,
        });
        toast.success(
          `Map ${mapName} was successfully boosted with many votes.`
        );
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
      enabled: !votemapStatus.enabled,
    });
  };

  return (
    <Stack direction={{ xs: "column-reverse", md: "row" }} spacing={1}>
      <MapListContainer>
        <Typography variant="h6">Current Selection</Typography>
        <MapList
          maps={votemapStatus.results.map((s) => s.map)}
          emptyListMessage={
            votemapStatus.enabled
              ? "There are no maps in the selection. Your configuration may be too restrictive."
              : "Votemap is disabled."
          }
          sort={false}
          renderItem={(mapLayer, index) => {
            return votemapStatus.player_choice && index === 0 ? (
              <Box sx={{ py: 2 }}>
                <Typography variant="subtitle2">
                  {votemapStatus.player_choice.player_name}'s choice
                </Typography>
                <MapVotemapListItem
                  key={mapLayer.id}
                  mapLayer={mapLayer}
                  voters={votemapStatus.results[index].voters}
                  votesCount={votemapStatus.results[index].votes_count}
                  onClick={removeMapFromVotemap}
                  isPlayerChoice={votemapStatus.player_choice}
                />
              </Box>
            ) : (
              <MapVotemapListItem
                key={mapLayer.id}
                mapLayer={mapLayer}
                voters={votemapStatus.results[index].voters}
                votesCount={votemapStatus.results[index].votes_count}
                onClick={removeMapFromVotemap}
                isPlayerChoice={votemapStatus.player_choice}
              />
            );
          }}
        />
        <Divider flexItem orientation="horizontal" sx={{ my: 1 }} />
        <Stack spacing={1}>
          <Typography variant="h6">History</Typography>
          {votemapResults.length > 0 ? (
            <>
              <Pagination
                size="small"
                count={votemapResults.length}
                page={resultHistoryPage}
                onChange={handleResultHistoryPageChange}
              />
              <Typography>
                Result recorded{" "}
                {dayjs
                  .unix(votemapResults[resultHistoryPage - 1].ts)
                  .format("lll")}{" "}
                with {votemapResults[resultHistoryPage - 1].map.pretty_name} on
                the server.
              </Typography>
              <MapList
                maps={votemapResults[resultHistoryPage - 1].results.map(
                  (s) => s.map
                )}
                emptyListMessage={
                  "There were no map options or the votemap was disabled"
                }
                sort={false}
                renderItem={(mapLayer, index) => (
                  <MapVotemapResultListItem
                    key={mapLayer.id}
                    mapLayer={mapLayer}
                    votesCount={
                      votemapResults[resultHistoryPage - 1].results[index]
                        .votes_count
                    }
                  />
                )}
              />
            </>
          ) : (
            <Typography>No historical data recorded yet.</Typography>
          )}
        </Stack>
      </MapListContainer>
      <ActionsContainer>
        <Typography variant="subtitle2" component={"div"}>
          Status: {votemapStatus.enabled ? `🟢 ENABLED` : `🔴 DISABLED`}
        </Typography>
        <Typography variant="subtitle2" component={"div"}>
          Next map:{" "}
          {votemapStatus.enabled ? votemapStatus.next_map ?? "TBD" : "N/A"}
        </Typography>
        <Typography variant="subtitle2" component={"div"}>
          Last vote reminder:{" "}
          {votemapStatus.last_reminder
            ? dayjs(votemapStatus.last_reminder).fromNow()
            : "N/A"}
        </Typography>
        <Divider orientation="horizontal" sx={{ my: 1 }} />
        <Stack direction="row" spacing={1} alignItems={"center"}>
          <Button
            onClick={handleVotemapToggle}
            startIcon={
              isToggling ? (
                <CircularProgress size={20} />
              ) : votemapStatus.enabled ? (
                <PowerOffIcon />
              ) : (
                <PowerIcon />
              )
            }
            variant="contained"
            disabled={isToggling}
            color={votemapStatus.enabled ? "error" : "success"}
            sx={{ minWidth: 120 }}
            size="small"
          >
            {votemapStatus.enabled ? "Disable" : "Enable"}
          </Button>
          <Typography variant="caption">
            {votemapStatus.enabled
              ? "votemap and decide the maps based on map rotation"
              : "votemap and decide maps dynamically on vote count or other conditions"}
          </Typography>
        </Stack>
        <Divider flexItem orientation="horizontal" sx={{ my: 1 }} />
        <Stack direction="row" spacing={1} alignItems={"center"}>
          <Button
            onClick={resetVotemap}
            disabled={isReseting || !votemapStatus.enabled}
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
            disabled={isSendingReminder || !votemapStatus.enabled}
            startIcon={
              isSendingReminder ? (
                <CircularProgress size={20} />
              ) : (
                <AnnouncementIcon />
              )
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
        <Divider flexItem orientation="horizontal" sx={{ my: 2 }} />
        <Stack spacing={2}>
          <Stack direction="row" spacing={1} alignItems={"center"}>
            <Button
              onClick={() => {
                addMapToVotemap(selectedMap);
              }}
              disabled={
                !selectedMap || isAddingMapToVotemap || !votemapStatus.enabled
              }
              startIcon={
                isAddingMapToVotemap ? (
                  <CircularProgress size={20} />
                ) : (
                  <AddIcon />
                )
              }
              variant="contained"
              sx={{ minWidth: 120 }}
              size="small"
            >
              Add
            </Button>
            <Typography variant="caption">
              new map to the current selection.
            </Typography>
          </Stack>
          <Stack direction="row" spacing={1} alignItems={"center"}>
            <Button
              onClick={() => {
                setVotemapWinner(selectedMap);
              }}
              disabled={
                !selectedMap || isSettingVotemapWinner || !votemapStatus.enabled
              }
              startIcon={
                isAddingMapToVotemap ? (
                  <CircularProgress size={20} />
                ) : (
                  <StarIcon />
                )
              }
              variant="contained"
              sx={{ minWidth: 120 }}
              size="small"
            >
              Set
            </Button>
            <Typography variant="caption">
              a map to be the next map by adding 999 votes.
            </Typography>
          </Stack>
          <MapAutocomplete
            options={maps}
            selected={selectedMap}
            onSelect={(newMapId) => setSelectedMap(newMapId)}
          />
        </Stack>
        <Divider flexItem orientation="horizontal" sx={{ my: 2 }} />
      </ActionsContainer>
    </Stack>
  );
}

export default VotemapStatusPage;
