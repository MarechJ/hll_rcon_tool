import { useState, useMemo } from "react";
import { extractPlayers, extractTeamState } from "@/utils/extractPlayers";
import {
  Box,
  Button,
  Stack,
  LinearProgress,
  Typography,
  IconButton,
  Tooltip,
} from "@mui/material";
import { ActionMenuButton } from "@/features/player-action/ActionMenu";
import { generatePlayerActions } from "@/features/player-action/actions";
import MoreHorizIcon from "@mui/icons-material/MoreHoriz";
import { useQuery } from "@tanstack/react-query";
import { teamsLiveQueryOptions } from "@/queries/teams-live-query";
import { TeamSection, UNASSIGNED } from "./team-section";
import { TeamContainer } from "./styled";
import { cmd } from "@/utils/fetchUtils";
import GameOverview from "@/components/game/overview";
import { OverviewSkeleton } from "./skeletons";
import PlaylistAddCheckIcon from "@mui/icons-material/PlaylistAddCheck";
import PlaylistRemoveIcon from "@mui/icons-material/PlaylistRemove";
import UnfoldLessDoubleIcon from "@mui/icons-material/UnfoldLessDouble";
import UnfoldMoreDoubleIcon from "@mui/icons-material/UnfoldMoreDouble";
import StickyContainer from "@/components/shared/StickyContainer";

const TeamViewPage = () => {
  const { data: teams, isFetching } = useQuery({
    ...teamsLiveQueryOptions,
    staleTime: 5 * 1000,
    refetchInterval: 10 * 1000,
  });

  const { data: gameState } = useQuery({
    queryKey: ["game", "state"],
    queryFn: cmd.GET_GAME_STATE,
    staleTime: 5 * 1000,
    refetchInterval: 10 * 1000,
  });

  const gameData = useMemo(() => {
    if (gameState && teams) {
      return {
        ...gameState,
        allies: {
          ...extractTeamState(teams?.allies ?? {}),
          ...(teams?.allies ?? {}),
        },
        axis: {
          ...extractTeamState(teams?.axis ?? {}),
          ...(teams?.axis ?? {}),
        },
        none: {
          ...extractTeamState(teams?.none ?? {}),
          ...(teams?.none ?? {}),
        },
      };
    }
    return null;
  }, [gameState, teams]);

  const [selectedPlayers, setSelectedPlayers] = useState(new Map());
  const [expandedSquads, setExpandedSquads] = useState({
    allies: { [UNASSIGNED]: true },
    axis: { [UNASSIGNED]: true },
    lobby: { [UNASSIGNED]: true },
  });

  const { axisTeam, alliesTeam, lobbyTeam } = useMemo(() => {
    return {
      axisTeam: extractTeamState(teams?.axis, "axis"),
      alliesTeam: extractTeamState(teams?.allies, "allies"),
      lobbyTeam: extractTeamState(teams?.none, "lobby"),
    };
  }, [teams]);

  // Get all squads from both teams
  const allSquads = useMemo(() => {
    const squads = {
      allies: new Set(),
      axis: new Set(),
      lobby: new Set(),
    };

    if (!alliesTeam || !axisTeam || !lobbyTeam) return squads;

    alliesTeam.squads.forEach((squad) => {
      if (squad.name !== "command") {
        squads.allies.add(squad.name);
      }
    });

    axisTeam.squads.forEach((squad) => {
      if (squad.name !== "command") {
        squads.axis.add(squad.name);
      }
    });

    lobbyTeam.squads.forEach((squad) => {
      squads.lobby.add(squad.name);
    });

    return squads;
  }, [alliesTeam, axisTeam, lobbyTeam]);

  const handleToggleSquad = (team, squadName) => {
    setExpandedSquads((prev) => ({
      ...prev,
      [team]: {
        ...prev[team],
        [squadName]: !prev[team]?.[squadName],
      },
    }));
  };

  const handleExpandAll = () => {
    const newState = { allies: {}, axis: {}, lobby: {} };
    Object.entries(allSquads).forEach(([team, squads]) => {
      squads.forEach((squadName) => {
        newState[team][squadName] = true;
      });
      newState[team][UNASSIGNED] = true;
    });
    setExpandedSquads(newState);
  };

  const handleCollapseAll = () => {
    const newState = { allies: {}, axis: {}, lobby: {} };
    Object.entries(allSquads).forEach(([team, squads]) => {
      squads.forEach((squadName) => {
        newState[team][squadName] = false;
      });
      newState[team][UNASSIGNED] = false;
    });
    setExpandedSquads(newState);
  };

  const handleTeamExpandAll = (team) => {
    const teamSquads = allSquads[team];
    setExpandedSquads((prev) => ({
      ...prev,
      [team]: Object.fromEntries(
        [...Array.from(teamSquads), UNASSIGNED].map((name) => [name, true])
      ),
    }));
  };

  const handleTeamCollapseAll = (team) => {
    const teamSquads = allSquads[team];
    setExpandedSquads((prev) => ({
      ...prev,
      [team]: Object.fromEntries(
        [...Array.from(teamSquads), UNASSIGNED].map((name) => [name, false])
      ),
    }));
  };

  const handleTogglePlayer = (player, event) => {
    event.stopPropagation();
    setSelectedPlayers((prev) => {
      const next = new Map(prev);
      if (next.has(player.player_id)) {
        next.delete(player.player_id);
      } else {
        next.set(player.player_id, {
          player_id: player.player_id,
          name: player.name,
        });
      }
      return next;
    });
  };

  const handleToggleSquadSelection = (players, isSelected) => {
    setSelectedPlayers((prev) => {
      const next = new Map(prev);
      if (!isSelected) {
        players.forEach((p) =>
          next.set(p.player_id, {
            player_id: p.player_id,
            name: p.name,
          })
        );
      } else {
        players.forEach((p) => next.delete(p.player_id));
      }
      return next;
    });
  };

  const handleToggleTeam = (players, selected) => {
    setSelectedPlayers((prev) => {
      const next = new Map(prev);
      if (selected) {
        players.forEach((p) =>
          next.set(p.player_id, {
            player_id: p.player_id,
            name: p.name,
          })
        );
      } else {
        players.forEach((p) => next.delete(p.player_id));
      }
      return next;
    });
  };

  const handleSelectAll = () => {
    const allPlayers = extractPlayers(teams);
    const allPlayersMap = new Map(
      allPlayers.map((p) => [
        p.player_id,
        { player_id: p.player_id, name: p.name },
      ])
    );
    setSelectedPlayers(allPlayersMap);
  };

  const handleUnselectAll = () => {
    setSelectedPlayers(new Map());
  };

  const getTeamSection = (team) => {
    const name = team?.name ?? "unknown";
    return (
      <TeamSection
        team={team}
        title={name.toUpperCase()}
        selectedPlayers={selectedPlayers}
        onTogglePlayer={handleTogglePlayer}
        onToggleSquad={handleToggleSquadSelection}
        onToggleAll={handleToggleTeam}
        expandedSquads={expandedSquads[name]}
        onToggleExpand={(squadName) => handleToggleSquad(name, squadName)}
        onTeamExpand={() => handleTeamExpandAll(name)}
        onTeamCollapse={() => handleTeamCollapseAll(name)}
      />
    );
  };

  return (
    <Box
      sx={{
        position: "relative",
        minHeight: "100%",
        display: "flex",
        flexDirection: "column",
        width: "100%",
      }}
    >
      {gameData ? (
        <GameOverview
          map={gameData.current_map}
          time={gameData.raw_time_remaining}
          allies={gameData.current_map.map.allies}
          axis={gameData.current_map.map.axis}
          mode={gameData.current_map.game_mode}
          mapName={gameData.current_map.pretty_name}
          axisCount={gameData.num_axis_players}
          alliesCount={gameData.num_allied_players}
          score={{ allies: gameData.allied_score, axis: gameData.axis_score }}
        />
      ) : (
        <OverviewSkeleton />
      )}
      <StickyContainer
        sx={{
          mb: 1,
          backgroundColor: "background.paper",
          borderBottom: "1px solid",
          borderColor: "divider",
        }}
      >
        <Stack
          direction="row"
          sx={{
            height: 40,
            "& > *": { height: "100%" },
            width: "100%",
            px: 2,
          }}
        >
          <ActionMenuButton
            actions={generatePlayerActions({
              multiAction: true,
              onlineAction: true,
            })}
            recipients={Array.from(selectedPlayers.values())}
            disabled={!selectedPlayers.size}
            renderButton={(props) => (
              <IconButton
                disabled={!selectedPlayers.size}
                aria-label="Apply Actions"
                {...props}
              >
                <MoreHorizIcon />
                <Box
                  component={"span"}
                  sx={{ display: { xs: "none", lg: "span" } }}
                >
                  Apply Actions
                </Box>
              </IconButton>
            )}
          />
          <Tooltip title="Select All">
            <span>
              <IconButton aria-label="Select All" onClick={handleSelectAll}>
                <PlaylistAddCheckIcon />
              </IconButton>
            </span>
          </Tooltip>
          <Tooltip title="Unselect All">
            <span>
              <IconButton aria-label="Unselect All" onClick={handleUnselectAll}>
                <PlaylistRemoveIcon />
              </IconButton>
            </span>
          </Tooltip>
          <Box sx={{ flexGrow: 1 }} />
          <Tooltip title="Expand All">
            <span>
              <IconButton aria-label="Expand All" onClick={handleExpandAll}>
                <UnfoldMoreDoubleIcon />
              </IconButton>
            </span>
          </Tooltip>
          <Tooltip title="Collapse All">
            <span>
              <IconButton aria-label="Collapse All" onClick={handleCollapseAll}>
                <UnfoldLessDoubleIcon />
              </IconButton>
            </span>
          </Tooltip>
        </Stack>
        <Box sx={{ height: 2 }}>
          {isFetching && <LinearProgress sx={{ height: 2 }} />}
        </Box>
      </StickyContainer>
      <TeamContainer>
        {getTeamSection(alliesTeam)}
        {getTeamSection(axisTeam)}
      </TeamContainer>
      <TeamContainer>{getTeamSection(lobbyTeam)}</TeamContainer>
    </Box>
  );
};

export default TeamViewPage;
