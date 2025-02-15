import {
  Card,
  CardHeader,
  CardContent,
  Box,
  Typography,
  List,
  ListItem,
  Stack,
  Tooltip,
} from "@mui/material";
import { useMemo } from "react";
import dayjs from "dayjs";

const isValidGame = (game) => {
  const MIN_GAME_DURATION = 10 * 60 * 1000;
  const MAX_GAME_DURATION = 200 * 60 * 1000;

  return (
    game.end && game.start &&
    game.result?.allied !== undefined && 
    game.result?.axis !== undefined &&
    ((new Date(game.end) - new Date(game.start)) >= MIN_GAME_DURATION) &&
    ((new Date(game.end) - new Date(game.start)) <= MAX_GAME_DURATION) &&
    (game.map.game_mode !== "control" && (game.result.allied + game.result.axis) === 5)
  );
}

const MapStatsCard = ({ games }) => {
  const mapStats = useMemo(() => {
    const invalidGames = [];
    const validGames = games.filter((game) => {
      if (!isValidGame(game)) {
        invalidGames.push(game);
        return false;
      }
      return true;
    });

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
    return 'secondary.main';
  };

  return (
    <Card>
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
              divider={true}
              sx={{
                display: 'flex',
                flexDirection: { xs: 'column', sm: 'row' },
                gap: { xs: 1, sm: 2 },
                py: 1,
              }}
            >
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: 1, 
                width: { xs: '100%', sm: '40%' },
                order: { xs: 2, sm: 1 }
              }}>
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
              
              <Box sx={{ 
                display: 'flex',
                width: { xs: '100%', sm: 'auto' },
                justifyContent: { xs: 'space-between', sm: 'flex-start' },
                alignItems: 'center',
                gap: { xs: 1, sm: 2 },
                order: { xs: 1, sm: 2 }
              }}>
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
                  ml: { xs: 0, sm: 'auto' },
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
                    <li>Have a final score that adds up to exactly 5 except for Skirmish</li>
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
    </Card>
  );
};

export default MapStatsCard; 