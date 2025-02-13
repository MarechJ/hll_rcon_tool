import { useState, useMemo } from "react";
import { extractPlayers, extractTeamState } from "@/utils/extractPlayers";
import {
  Box,
  Button,
  Stack,
  LinearProgress,
} from "@mui/material";
import { ActionMenuButton } from "@/features/player-action/ActionMenu";
import { generatePlayerActions } from "@/features/player-action/actions";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import { useQuery } from "@tanstack/react-query";
import { teamsLiveQueryOptions } from "@/queries/teams-live-query";
import { TeamSection, UNASSIGNED } from "./team-section";
import { TeamContainer } from "./styled";

const TeamViewPage = () => {
  const { data: teams, isFetching } = useQuery({
    ...teamsLiveQueryOptions,
    staleTime: 5 * 1000,
    refetchInterval: 10 * 1000,
  });

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
      lobbyTeam: extractTeamState(teams?.null, "lobby"),
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
    
    alliesTeam.squads.forEach(squad => {
      if (squad.name !== "command") {
        squads.allies.add(squad.name);
      }
    });
    
    axisTeam.squads.forEach(squad => {
      if (squad.name !== "command") {
        squads.axis.add(squad.name);
      }
    });

    lobbyTeam.squads.forEach(squad => {
      squads.lobby.add(squad.name);
    });
    
    return squads;
  }, [alliesTeam, axisTeam, lobbyTeam]);

  const handleToggleSquad = (team, squadName) => {
    setExpandedSquads(prev => ({
      ...prev,
      [team]: {
        ...prev[team],
        [squadName]: !prev[team]?.[squadName]
      }
    }));
  };

  const handleExpandAll = () => {
    const newState = { allies: {}, axis: {}, lobby: {} };
    Object.entries(allSquads).forEach(([team, squads]) => {
      squads.forEach(squadName => {
        newState[team][squadName] = true;
      });
      newState[team][UNASSIGNED] = true;
    });
    setExpandedSquads(newState);
  };

  const handleCollapseAll = () => {
    const newState = { allies: {}, axis: {}, lobby: {} };
    Object.entries(allSquads).forEach(([team, squads]) => {
      squads.forEach(squadName => {
        newState[team][squadName] = false;
      });
      newState[team][UNASSIGNED] = false;
    });
    setExpandedSquads(newState);
  };

  const handleTeamExpandAll = (team) => {
    const teamSquads = allSquads[team];
    setExpandedSquads(prev => ({
      ...prev,
      [team]: Object.fromEntries([
        ...Array.from(teamSquads),
        UNASSIGNED
      ].map(name => [name, true]))
    }));
  };

  const handleTeamCollapseAll = (team) => {
    const teamSquads = allSquads[team];
    setExpandedSquads(prev => ({
      ...prev,
      [team]: Object.fromEntries([
        ...Array.from(teamSquads),
        UNASSIGNED
      ].map(name => [name, false]))
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
    const allPlayers = extractPlayers(teams)
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
    )
  }

  return (
    <Stack>
      <Stack
        direction="row"
        sx={{
          backgroundColor: "background.paper",
          borderBottom: "1px solid divider",
          height: 40,
          "& > *": { height: "100%" },
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
            <Button
              sx={{ width: 170 }}
              startIcon={<MoreVertIcon />}
              disabled={!selectedPlayers.size}
              {...props}
            >
              Apply Actions 
            </Button>
          )}
        />
        <Button onClick={handleSelectAll}>Select All</Button>
        <Button onClick={handleUnselectAll}>Unselect All</Button>
        <Button onClick={handleExpandAll}>Expand All</Button>
        <Button onClick={handleCollapseAll}>Collapse All</Button>
      </Stack>
      <Box sx={{ height: 2 }}>
        {isFetching && <LinearProgress sx={{ height: 2 }} />}
      </Box>
      <TeamContainer> 
        {getTeamSection(axisTeam)}
        {getTeamSection(alliesTeam)}
      </TeamContainer>
      <TeamContainer>
        {getTeamSection(lobbyTeam)}
      </TeamContainer>
    </Stack>
  );
};

export default TeamViewPage;
