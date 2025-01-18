import { extractTeamState } from "@/utils/extractPlayers";
import { Box, Divider, Stack, Typography } from "@mui/material";
import WarningIcon from "@mui/icons-material/Warning";
// 
const InfoPanel = ({ gameData, playersData }) => {
  const content = [];

  const vipsCount = playersData.filter((player) => player.is_vip).length;
  if (vipsCount > 0) {
    content.push({
      type: "info",
      label: "VIPs",
      value: vipsCount,
    });
  }

  const watchedCount = playersData.filter((player) => player.profile.watchlist?.is_watched).length;
  if (watchedCount > 0) {
    content.push({
      type: "info",
      label: "Watched",
      value: watchedCount,
    });
  }

  const teamStates = {
    axis: gameData?.axis ? extractTeamState(gameData?.axis) : null,
    allies: gameData?.allies ? extractTeamState(gameData?.allies) : null,
    lobby: gameData?.none ? extractTeamState(gameData?.none) : null,
  }

  for (const team in teamStates) {
    if (team !== "lobby" && playersData.length > 0 && teamStates[team] && teamStates[team].armycommander === 0) {
      content.push({
        type: "warning",
        label: `${team.charAt(0).toUpperCase() + team.slice(1)}`,
        value: "No Commander",
      });
    }

    if (team !== "lobby" && playersData.length > 0 && teamStates[team] && teamStates[team].no_sl_squads.length > 0) {
      content.push({
        type: "warning",
        label: `${team.charAt(0).toUpperCase() + team.slice(1)} No SL`,
        value: teamStates[team].no_sl_squads.map((squad) => squad.toUpperCase()).join(", "),
      });
    }

    if (teamStates[team] && teamStates[team].players_in_lobby.length > 0) {
      content.push({
        type: "info",
        label: team !== "lobby" ? `${team.charAt(0).toUpperCase() + team.slice(1)} Lobby` : "All Lobby",
        value: teamStates[team].players_in_lobby.length,
      });
    }
  }

  content.push({
    type: "info",
    label: "Next Map",
    value: gameData?.next_map.pretty_name,
  });

  return (
    <Stack direction="row" flexWrap="wrap" alignItems="center" columnGap={1} divider={<Divider orientation="vertical" flexItem />}  sx={{ backgroundColor: "background.paper", border: "1px solid theme.palette.divider", p: 0.5 }}> 
      {content.sort((a) => a.type === "warning" ? -1 : 1).map((item, index) => (
        <Box key={index} sx={{ display: "flex", alignItems: "center", gap: 0.5, textWrap: "nowrap" }}>
          {item.type === "warning" && <WarningIcon sx={{ color: "warning.main", fontSize: 12 }} />}
          <Typography variant="caption">{item.label}: {item.value}</Typography>
        </Box>
      ))}
    </Stack>
  );
};

export default InfoPanel;
