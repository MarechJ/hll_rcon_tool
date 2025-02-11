import { useGlobalStore } from "@/hooks/useGlobalState";
import { cmd } from "@/utils/fetchUtils";
import {
  List,
  Card,
  ListItem,
  CardHeader,
  CardContent,
  styled,
  Box,
  Typography,
  Divider,
  Stack,
  Tooltip,
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
import { gameQueryOptions } from "@/queries/game-query";
import Emoji from "@/components/shared/Emoji";

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
    .map((game) => game.result?.allied ?? 0 - game.result?.axis ?? 0)
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
                    flexGrow: 1,
                    maxWidth: "50%",
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
                <Typography variant="subtitle2" sx={{ fontSize: 20, whiteSpace: "nowrap" }}>
                  {game.result?.allied ?? "?"} - {game.result?.axis ?? "?"}
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

const MapStatsCard = ({ games }) => {
  const mapStats = useMemo(() => {
    const MIN_GAME_DURATION = 10 * 60 * 1000;
    const MAX_GAME_DURATION = 200 * 60 * 1000;
    const validGames = games.filter(game => 
      game.end && game.start &&
      game.result?.allied !== undefined && 
      game.result?.axis !== undefined &&
      ((new Date(game.end) - new Date(game.start)) >= MIN_GAME_DURATION) &&
      ((new Date(game.end) - new Date(game.start)) <= MAX_GAME_DURATION) &&
      ((game.result.allied + game.result.axis) === 5)
    );
    const discardedGames = games.length - validGames.length;

    // Get oldest game date
    const oldestGame = validGames.length > 0 ? 
      new Date(Math.min(...validGames.map(game => new Date(game.start)))) : null;

    // Calculate games per day
    const gamesPerDay = validGames.reduce((acc, game) => {
      const date = dayjs(game.start).format('YYYY-MM-DD');
      if (!acc[date]) acc[date] = 0;
      acc[date]++;
      return acc;
    }, {});

    // Calculate games per mode
    const gamesPerMode = validGames.reduce((acc, game) => {
      const mode = game.map.game_mode;
      if (!acc[mode]) acc[mode] = 0;
      acc[mode]++;
      return acc;
    }, {});

    // Convert to array and add day of week with date
    const dailyStats = Object.entries(gamesPerDay)
      .map(([date, count]) => ({
        date,
        dayOfWeek: dayjs(date).format('ddd'),
        formattedDate: dayjs(date).format('DD/MM'),
        count
      }))
      .sort((a, b) => b.date.localeCompare(a.date));

    // Convert modes to array and capitalize
    const modeStats = Object.entries(gamesPerMode)
      .map(([mode, count]) => ({
        mode: mode[0].toUpperCase() + mode.slice(1),
        count
      }))
      .sort((a, b) => b.count - a.count);

    const stats = validGames.reduce((acc, game) => {
      const mapName = game.map.map.pretty_name;
      const duration = new Date(game.end) - new Date(game.start);
      
      if (!acc[mapName]) {
        acc[mapName] = {
          mapName,
          imageName: game.map.image_name,
          totalGames: 0,
          alliedWins: 0,
          axisWins: 0,
          totalDuration: 0,
        };
      }
      
      acc[mapName].totalGames++;
      acc[mapName].totalDuration += duration;
      if (game.result?.allied > game.result?.axis) {
        acc[mapName].alliedWins++;
      } else if (game.result?.allied < game.result?.axis) {
        acc[mapName].axisWins++;
      }
      return acc;
    }, {});

    return {
      discardedGames,
      totalValidGames: validGames.length,
      oldestGame,
      dailyStats,
      modeStats,
      stats: Object.values(stats)
        .map(stat => ({
          ...stat,
          averageDuration: Math.round(stat.totalDuration / stat.totalGames / 60000),
          alliedWinRate: (stat.alliedWins / stat.totalGames * 100).toFixed(1),
          axisWinRate: (stat.axisWins / stat.totalGames * 100).toFixed(1),
        }))
        .sort((a, b) => b.totalGames - a.totalGames)
    };
  }, [games]);

  // Helper function to calculate color intensity based on win rate
  const getWinRateColor = (winRate, baseColor) => {
    const rate = parseFloat(winRate);
    if (rate === 50) return 'text.primary';
    const intensity = Math.min(Math.abs(rate - 50) / 50, 1);
    return `${baseColor}.${Math.round(intensity * 800)}`;
  };

  // Helper function to get duration color
  const getDurationColor = (duration) => {
    if (duration < 20) return 'error.main';
    if (duration < 35) return 'warning.main';
    if (duration < 50) return 'warning.light';
    if (duration < 75) return 'success.main';
    return 'secondary.main'; // purple in default MUI theme
  };

  return (
    <StyledCard>
      <CardHeader 
        title="Map Statistics" 
        subheader={
          <Stack spacing={0.5}>
            <Typography variant="caption" component="div">
              Games per day:
              {mapStats.dailyStats.map(stat => (
                <Box key={stat.date} component="span" sx={{ ml: 1 }}>
                  {stat.dayOfWeek} ({stat.formattedDate}):
                  <Typography 
                    component="span" 
                    variant="body2" 
                    sx={{ 
                      ml: 0.5,
                      fontWeight: 500,
                      color: 'text.primary'
                    }}
                  >
                    {stat.count}
                  </Typography>
                </Box>
              ))}
            </Typography>
            <Typography variant="caption" component="div">
              Game modes:
              {mapStats.modeStats.map(stat => (
                <Box key={stat.mode} component="span" sx={{ ml: 1 }}>
                  {stat.mode}:
                  <Typography 
                    component="span" 
                    variant="body2" 
                    sx={{ 
                      ml: 0.5,
                      fontWeight: 500,
                      color: 'text.primary'
                    }}
                  >
                    {stat.count}
                  </Typography>
                </Box>
              ))}
            </Typography>
          </Stack>
        }
      />
      <CardContent>
        <List dense sx={{ minWidth: 300 }}>
          {mapStats.stats.map((stat) => (
            <ListItem
              key={stat.mapName}
              sx={{
                display: 'flex',
                gap: 2,
                py: 1,
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '40%' }}>
                <img
                  src={"/maps/icons/" + stat.imageName}
                  width={40}
                  height={22.5}
                  alt=""
                  style={{ borderRadius: 2 }}
                />
                <Box>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                    {stat.mapName}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <Typography variant="caption" color="text.secondary">
                      avg:
                    </Typography>
                    <Typography 
                      variant="caption" 
                      sx={{ 
                        fontWeight: 500,
                        color: (theme) => getDurationColor(stat.averageDuration)
                      }}
                    >
                      {stat.averageDuration} min
                    </Typography>
                  </Box>
                </Box>
              </Box>
              
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <Typography variant="caption" color="text.secondary">
                  Played:
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>
                  {stat.totalGames}
                </Typography>
              </Box>

              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: 2,
                ml: 'auto',
                '& .team': {
                  display: 'flex',
                  alignItems: 'center',
                  gap: 0.5,
                }
              }}>
                <Box className="team">
                  <Typography variant="caption">Allies:</Typography>
                  <Typography 
                    variant="body2" 
                    sx={{ 
                      fontWeight: 500,
                      color: (theme) => getWinRateColor(stat.alliedWinRate, 'success')
                    }}
                  >
                    {stat.alliedWinRate}%
                  </Typography>
                </Box>
                <Box className="team">
                  <Typography variant="caption">Axis:</Typography>
                  <Typography 
                    variant="body2" 
                    sx={{ 
                      fontWeight: 500,
                      color: (theme) => getWinRateColor(stat.axisWinRate, 'error')
                    }}
                  >
                    {stat.axisWinRate}%
                  </Typography>
                </Box>
              </Box>
            </ListItem>
          ))}
        </List>
        <Box sx={{ 
          mt: 2, 
          pt: 1, 
          borderTop: 1, 
          borderColor: 'divider',
          color: 'text.secondary'
        }}>
          <Stack spacing={0.5}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <Typography variant="caption">
                Based on {mapStats.totalValidGames} valid games since {
                  mapStats.oldestGame ? dayjs(mapStats.oldestGame).format('ddd, MMM D') : 'N/A'
                }
              </Typography>
              <Tooltip title={
                <Typography variant="caption">
                  A valid game must:
                  <ul style={{ margin: '4px 0', paddingLeft: '16px' }}>
                    <li>Have a duration between 10 and 200 minutes</li>
                    <li>Have a final score that adds up to exactly 5</li>
                    <li>Have complete data for both teams</li>
                  </ul>
                </Typography>
              }>
                <Box component="span" 
                  sx={{ 
                    cursor: 'help',
                    display: 'inline-flex',
                    alignItems: 'center'
                  }}
                >
                  ⓘ
                </Box>
              </Tooltip>
            </Box>
            {mapStats.discardedGames > 0 && 
              <Typography variant="caption">
                {mapStats.discardedGames} invalid games excluded
              </Typography>
            }
          </Stack>
        </Box>
      </CardContent>
    </StyledCard>
  );
};

const Dashboard = () => {
  const status = useGlobalStore((state) => state.status);
  const onlineCrconMods = useGlobalStore((state) => state.onlineCrconMods);
  const onlineIngameMods = useGlobalStore((state) => state.onlineIngameMods);
  const onlinePlayers = useGlobalStore((state) => state.onlinePlayers);

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
      label: <Stack direction={"row"} alignItems={"center"} spacing={0.5}>
        <Emoji emoji={flag} size={16} />
        <Typography variant="subtitle2">({players.length})</Typography>
      </Stack>,
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
    },
  });

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
        label: `Admin (${adminLogs.length})`,
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
          title="VIPs & Watched"
          onlineUsers={[
            { group: "VIP", label: `VIP (${vips.length})`, users: vips },
            { group: "Watched", label: `Watched (${watchedPlayers.length})`, users: watchedPlayers },
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
            { group: "CRCON", label: `CRCON (${crconMods.length})`, users: crconMods, manageLink: "/admin" },
            {
              group: "In-Game",
              label: `In-Game (${ingameMods.length})`,
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
        <GamesCard games={gamesList.slice(0, 15)} />
      </Grid>

      <Grid size={MEDIUM_CARD_SIZE}>
        <MapStatsCard games={gamesList} />
      </Grid>

    </Grid>
  );
};

export default Dashboard;
