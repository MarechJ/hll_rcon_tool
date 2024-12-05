import { useAuth } from "@/hooks/useAuth";
import { useGlobalStore } from "@/hooks/useGlobalState";
import { cmd } from "@/utils/fetchUtils";
import {
  List,
  ListItemAvatar,
  Card,
  Avatar,
  ListItem,
  ListItemText,
  CardHeader,
  CardContent,
  styled,
  Box,
  Typography,
  Divider,
} from "@mui/material";
import Grid from "@mui/material/Grid2";
import { Link } from "react-router-dom";
import { useMemo } from "react";
import { useQuery, useQueries } from "@tanstack/react-query";
import { LineChart } from "@mui/x-charts";
import dayjs from "dayjs";
import OnlineUsersCard from "@/components/shared/card/UsersCard";
import LogsCard from "@/components/shared/card/LogsCard";
import ScrollableCard from "@/components/shared/card/ScrollableCard";
import { MapAvatar } from "@/components/MapManager/map-details";

const CHART_HEIGHT = 275;

const SMALL_CARD_SIZE = {
  xs: 12,
  sm: 6,
  xl: 3,
};

const MEDIUM_CARD_SIZE = {
  xs: 12,
  md: 6,
};

const LARGE_CARD_SIZE = {
  xs: 12,
};

const StyledCard = styled(Card)({
  margin: "0 auto",
  width: "100%",
});

const TotalPlayersCard = ({ games }) => {
  const players = games.map((game) => game.player_stats?.length ?? 0).reverse();
  const times = games.map((game) => new Date(game.start)).reverse();

  return (
    <StyledCard sx={{ height: "100%" }}>
      <CardHeader title="Total Players" />
      <CardContent>
        <LineChart
          xAxis={[
            {
              data: times,
              scaleType: "band",
              valueFormatter: (value) =>
                dayjs(value).format("DD/MM/YYYY HH:mm"),
            },
          ]}
          series={[
            {
              data: players,
              valueFormatter: (value) => `${value} players`,
            },
          ]}
          height={CHART_HEIGHT}
        />
      </CardContent>
    </StyledCard>
  );
};

const GameBalanceCard = ({ games }) => {
  const times = games.map((game) => new Date(game.start)).reverse();
  const scores = games
    .map((game) => game.result.allied - game.result.axis)
    .reverse();

  return (
    <StyledCard sx={{ height: "100%" }}>
      <CardHeader title="Team Balance" />
      <CardContent>
        <LineChart
          xAxis={[
            {
              data: times,
              scaleType: "band",
              valueFormatter: (value) =>
                dayjs(value).format("DD/MM/YYYY HH:mm"),
            },
          ]}
          yAxis={[
            {
              min: -5,
              max: 5,
            },
          ]}
          series={[
            {
              data: scores,
              valueFormatter: (value) =>
                value === 0
                  ? "Unfinished game"
                  : value > 0
                  ? "Allies win"
                  : "Axis win",
            },
          ]}
          height={CHART_HEIGHT}
        />
      </CardContent>
    </StyledCard>
  );
};

const GamesCard = ({ games }) => {
  return (
    <Card>
      <CardHeader title="Last 15 Games" />
      <CardContent>
        <List dense sx={{ minWidth: 300 }}>
          {games.map((game) => {
            const size = 60;
            const ratio = 9 / 16;
            const matchMap = game.map;

            return (
              <ListItem
                key={game.id}
                component={Link}
                to={`/stats/games/${game.id}`}
                sx={{
                  "&:hover": { backgroundColor: "action.hover" },
                  color: "text.primary",
                }}
              >
                <Box
                  sx={{
                    display: "flex",
                    flexDirection: "row",
                    gap: 0.5,
                    width: "max-content",
                  }}
                >
                  <img
                    src={"/maps/icons/" + matchMap.image_name}
                    width={size}
                    height={size * ratio}
                    alt=""
                  />
                  <Box sx={{ display: "flex", flexDirection: "column" }}>
                    <Typography
                      variant="body1"
                      sx={{ fontWeight: 600, lineHeight: 1 }}
                    >
                      {matchMap.map.pretty_name}
                    </Typography>
                    <Typography
                      variant="subtitle2"
                      sx={{
                        display: "flex",
                        flexDirection: "row",
                        fontWeight: 400,
                      }}
                    >
                      <Box component="span" sx={{ paddingRight: 0.5 }}>
                        {matchMap.game_mode[0].toUpperCase() +
                          matchMap.game_mode.slice(1)}
                      </Box>
                      <Box component="span">{matchMap.environment}</Box>
                    </Typography>
                  </Box>
                </Box>
                <Divider orientation="vertical" flexItem sx={{ mx: 2 }} />
                <Typography variant="subtitle2" sx={{ fontSize: 20 }}>
                  {game.result.allied} - {game.result.axis}
                </Typography>
                <Divider orientation="vertical" flexItem sx={{ mx: 2 }} />
                <Typography variant="subtitle2">
                  {dayjs(game.start).format("HH:mm:ss, MMM DD")}
                </Typography>
              </ListItem>
            );
          })}
        </List>
      </CardContent>
    </Card>
  );
};

const Dashboard = () => {
  const status = useGlobalStore((state) => state.status);
  const onlineCrconMods = useGlobalStore((state) => state.onlineCrconMods);
  const onlineIngameMods = useGlobalStore((state) => state.onlineIngameMods);
  const onlinePlayers = useGlobalStore((state) => state.onlinePlayers);

  console.log(status);

  const vips = useMemo(
    () =>
      onlinePlayers
        .filter((player) => player.is_vip)
        .map((player) => ({
          id: player.player_id,
          name: player.name,
          avatar: player.profile?.steaminfo?.profile?.avatar,
        })),
    [onlinePlayers]
  );

  const watchedPlayers = useMemo(
    () =>
      onlinePlayers.filter((player) => player?.profile?.watchlist?.is_watched),
    [onlinePlayers]
  );

  const ingameMods = useMemo(
    () =>
      onlineIngameMods.map((mod) => ({
        id: mod.id,
        name: mod.username,
        avatar: onlinePlayers.find(
          (player) => player.player_id === mod.player_id
        )?.profile?.steaminfo?.profile?.avatar,
      })),
    [onlineIngameMods]
  );

  const crconMods = useMemo(
    () =>
      onlineCrconMods.map((mod) => ({
        id: mod.id,
        name: mod.username,
        avatar: onlinePlayers.find(
          (player) => player.player_id === mod.player_id
        )?.profile?.steaminfo?.profile?.avatar,
      })),
    [onlineCrconMods]
  );

  const playersGroupedByFlags = useMemo(() => {
    return Object.entries(
      onlinePlayers.reduce((acc, player) => {
        const flags = player.profile?.flags?.map((flag) => flag.flag);
        flags.forEach((flag) => {
          acc[flag] = (acc[flag] || []).concat({
            id: player.player_id,
            name: player.name,
            avatar: player.profile?.steaminfo?.profile?.avatar,
          });
        });
        return acc;
      }, {})
    ).map(([flag, players]) => ({
      group: flag,
      users: players,
    }));
  }, [onlinePlayers]);

  const { data: gamesList = [], isLoading: isLoadingGames } = useQuery({
    queryKey: ["games", "dashboard"],
    enabled: status !== null,
    queryFn: async () => {
      const result = await cmd.GET_COMPLETED_GAMES({
        params: { page: 1, limit: 100 },
      });
      if (!result?.maps) return [];

      return result.maps
        .filter((game) => game.server_number === status.server_number)
        .slice(0, 15);
    },
  });

  const gameQueries = useQueries({
    queries: gamesList.map((game) => ({
      queryKey: ["game", "details", game.id],
      staleTime: Infinity,
      queryFn: async () => {
        const details = await cmd.GET_COMPLETED_GAME_DETAIL({
          params: { map_id: game.id },
        });
        return details;
      },
      enabled: status !== null,
    })),
  });

  const detailedGames = useMemo(() => {
    return gameQueries
      .filter((query) => query.isSuccess)
      .map((query) => query.data);
  }, [gameQueries]);

  const { data: logs = [] } = useQuery({
    queryKey: ["logs", "dashboard"],
    queryFn: async () => {
      const rawLogs = await cmd.GET_LIVE_LOGS({
        payload: {
          end: 15000,
          filter_action: [],
          filter_player: [],
          inclusive_filter: true,
        },
      });

      const logs = Object.entries(
        rawLogs.result.logs.reduce((acc, log) => {
          acc[log.action] = (acc[log.action] || []).concat(log);
          return acc;
        }, {})
      ).map(([action, logs]) => ({
        group: action,
        logs: logs.slice(0, 100).map((log) => ({
          user_1: {
            id: log.player_id_1,
            name: log.player_name_1,
          },
          user_2: {
            id: log.player_id_2,
            name: log.player_name_2,
          },
          message: log.message,
          timestamp: log.timestamp_ms,
          action: log.action,
        })),
      }));

      const adminLogs = rawLogs.result.logs
        .filter(
          (log) =>
            log.action.startsWith("CHAT") && log.message.includes("!admin")
        )
        .map((log) => ({
          user_1: {
            id: log.player_id_1,
            name: log.player_name_1,
          },
          user_2: {
            id: log.player_id_2,
            name: log.player_name_2,
          },
          message: log.message,
          timestamp: log.timestamp_ms,
          action: log.action,
        }));

      logs.push({
        group: "ADMIN",
        logs: adminLogs,
      });

      return logs;
    },
  });

  const { data: mapRotation = [] } = useQuery({
    queryKey: ["map-rotation"],
    queryFn: async () => await cmd.GET_MAP_ROTATION(),
  });

  return (
    <Grid container sx={{ overflow: "hidden" }} spacing={2}>
      <Grid size={SMALL_CARD_SIZE}>
        <OnlineUsersCard
          title="Online"
          onlineUsers={[
            { group: "VIP", users: vips },
            { group: "Watched", users: watchedPlayers },
          ]}
        />
      </Grid>
      <Grid size={SMALL_CARD_SIZE}>
        <OnlineUsersCard title="Flagged" onlineUsers={playersGroupedByFlags} />
      </Grid>

      <Grid size={SMALL_CARD_SIZE}>
        <OnlineUsersCard
          title="Moderators"
          onlineUsers={[
            { group: "CRCON", users: crconMods, manageLink: "/admin" },
            {
              group: "In-Game",
              users: ingameMods,
              manageLink: "/settings/console-admins",
            },
          ]}
        />
      </Grid>

      <Grid size={SMALL_CARD_SIZE}>
        <ScrollableCard title="Map Rotation">
          <Box component="ol" sx={{ listStylePosition: "inside", pl: 0 }}>
            {mapRotation.map((map) => (
              <Box
                component="li"
                key={map.id}
                sx={{ display: "flex", alignItems: "center", gap: 1, mb: 0.25 }}
              >
                <MapAvatar mapLayer={map} sx={{ width: 24, height: 24 }} />
                <Typography variant="subtitle2">{map.pretty_name}</Typography>
              </Box>
            ))}
          </Box>
        </ScrollableCard>
      </Grid>

      <Grid size={LARGE_CARD_SIZE}>
        <LogsCard logs={logs} />
      </Grid>

      <Grid size={MEDIUM_CARD_SIZE}>
        <GamesCard games={detailedGames} />
      </Grid>

      <Grid container size={MEDIUM_CARD_SIZE} spacing={2}>
        <Grid size={LARGE_CARD_SIZE}>
          <TotalPlayersCard games={detailedGames} />
        </Grid>
        <Grid size={LARGE_CARD_SIZE}>
          <GameBalanceCard games={detailedGames} />
        </Grid>
      </Grid>
    </Grid>
  );
};

export default Dashboard;
