import {
  List,
  Card,
  ListItem,
  CardHeader,
  CardContent,
  Box,
  Typography,
} from "@mui/material";
import { Link } from "react-router-dom";
import dayjs from "dayjs";

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
            const duration = game.end && game.start ? 
              Math.round((new Date(game.end) - new Date(game.start)) / 60000) : null;

            // Helper function to get duration color
            const getDurationColor = (duration) => {
              if (!duration) return 'text.secondary';
              if (duration < 20) return 'error.main';
              if (duration < 35) return 'warning.main';
              if (duration < 50) return 'warning.light';
              if (duration < 75) return 'success.main';
              return 'secondary.main';
            };

            return (
              <ListItem
                key={game.id}
                component={Link}
                to={`/stats/games/${game.id}`}
                sx={{
                  "&:hover": { backgroundColor: "action.hover" },
                  color: "text.primary",
                  gap: 2,
                }}
              >
                <Box
                  sx={{
                    display: "flex",
                    flexDirection: "row",
                    gap: 1,
                    width: "40%",
                  }}
                >
                  <img
                    src={"/maps/icons/" + matchMap.image_name}
                    width={size}
                    height={size * ratio}
                    alt=""
                    style={{ borderRadius: 2 }}
                  />
                  <Box sx={{ display: "flex", flexDirection: "column" }}>
                    <Typography
                      variant="body1"
                      sx={{ fontWeight: 600, lineHeight: 1 }}
                    >
                      {matchMap.map.pretty_name}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <Typography
                        variant="subtitle2"
                        sx={{
                          px: 0.75,
                          py: 0.25,
                          bgcolor: 'action.selected',
                          borderRadius: 1,
                          fontSize: '0.75rem',
                          fontWeight: 500,
                        }}
                      >
                        {matchMap.game_mode[0].toUpperCase() + matchMap.game_mode.slice(1)}
                      </Typography>
                      <Typography
                        variant="caption"
                        sx={{ 
                          color: (theme) => getDurationColor(duration),
                          fontWeight: 500,
                        }}
                      >
                        {duration ? `${duration} min` : 'In Progress'}
                      </Typography>
                    </Box>
                  </Box>
                </Box>

                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: 0.5,
                  ml: 'auto'
                }}>
                  <Typography 
                    variant="h6" 
                    sx={{ 
                      whiteSpace: "nowrap",
                      color: game.result?.allied > game.result?.axis ? 'success.main' : 
                             game.result?.allied < game.result?.axis ? 'error.main' : 
                             'text.primary'
                    }}
                  >
                    {game.result?.allied ?? "?"} - {game.result?.axis ?? "?"}
                  </Typography>
                </Box>

                <Typography 
                  variant="subtitle2" 
                  sx={{ 
                    color: 'text.secondary',
                    whiteSpace: "nowrap",
                    minWidth: 140,
                  }}
                >
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

export default GamesCard; 