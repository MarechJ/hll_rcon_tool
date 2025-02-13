import { useState, useMemo } from "react";
import { extractPlayers, extractTeamState } from "@/utils/extractPlayers";
import { getPlayerTier, tierColors } from "@/utils/lib";
import teamViewResult from "./team-view.json";
import {
  Box,
  Typography,
  IconButton,
  Collapse,
  Checkbox,
  Button,
  Stack,
  CircularProgress,
  LinearProgress,
} from "@mui/material";
import { styled } from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import PersonOffIcon from "@mui/icons-material/PersonOff";
import StarIcon from "@mui/icons-material/Star";
import { usePlayerSidebar } from "@/hooks/usePlayerSidebar";
import { ActionMenuButton } from "@/features/player-action/ActionMenu";
import { generatePlayerActions } from "@/features/player-action/actions";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import { useQuery } from "@tanstack/react-query";
import { teamsLiveQueryOptions } from "@/queries/teams-live-query";

const UNASSIGNED = "null";

const TeamContainer = styled(Box)(({ theme }) => ({
  display: "flex",
  gap: theme.spacing(2),
  flexDirection: "row",
  [theme.breakpoints.down("lg")]: {
    flexDirection: "column",
  },
  fontFamily: "Roboto Mono, monospace",
  backgroundColor: theme.palette.background.default,
  padding: theme.spacing(2),
  width: "100%",
  overflow: "hidden",
}));

const TeamBox = styled(Box)(({ theme }) => ({
  flex: 1,
  borderRadius: theme.shape.borderRadius,
  minWidth: 0,
  display: "flex",
  flexDirection: "column",
  overflow: "hidden",
}));

const ScrollContainer = styled(Box)({
  overflowX: "auto",
  flex: 1,
  display: "flex",
  flexDirection: "column",
});

const ContentWrapper = styled(Box)({
  minWidth: "min-content",
});

const gridTemplateColumns = {
  default: "35px minmax(200px, 300px) 60px repeat(6, 60px)",
  sm: "35px minmax(150px, 200px) 60px repeat(6, 60px)",
};

const SquadHeader = styled(Box)(({ theme, selected }) => ({
  padding: theme.spacing(0.5, 1),
  backgroundColor: theme.palette.background.paper,
  borderBottom: `1px solid ${theme.palette.divider}`,
  display: "grid",
  gridTemplateColumns: gridTemplateColumns.default,
  alignItems: "center",
  cursor: "pointer",
  "&:hover": {
    backgroundColor: selected
      ? theme.palette.action.selected
      : theme.palette.action.hover,
  },
  "& .squad-info": {
    gridColumn: "1 / 3",
    display: "flex",
    alignItems: "center",
    gap: theme.spacing(1),
    minWidth: 0,
    "& .squad-name-container": {
      display: "flex",
      alignItems: "center",
      gap: theme.spacing(1),
      minWidth: 0,
      flex: 1,
      "& .MuiTypography-root": {
        color: selected ? theme.palette.primary.main : "inherit",
      },
    },
  },
  "& .squad-stats": {
    display: "contents",
    "& .stat": {
      textAlign: "right",
      fontFamily: "Roboto Mono, monospace",
      whiteSpace: "nowrap",
      fontSize: "0.75rem",
      color: selected
        ? theme.palette.primary.main
        : theme.palette.text.secondary,
    },
  },
  [theme.breakpoints.down("sm")]: {
    gridTemplateColumns: gridTemplateColumns.sm,
  },
}));

const PlayerRow = styled(Box)(({ theme, selected, level }) => ({
  display: "grid",
  gridTemplateColumns: gridTemplateColumns.default,
  padding: theme.spacing(0.5, 1),
  alignItems: "center",
  borderBottom: `1px solid ${theme.palette.divider}`,
  backgroundColor: theme.palette.background.paper,
  cursor: "pointer",
  "&:hover": {
    backgroundColor: selected
      ? theme.palette.action.selected
      : theme.palette.action.hover,
  },
  "& .stat": {
    textAlign: "right",
    fontFamily: "Roboto Mono, monospace",
    whiteSpace: "nowrap",
    color: selected ? theme.palette.primary.main : "inherit",
  },
  "& .player-info": {
    display: "flex",
    alignItems: "center",
    gap: theme.spacing(1),
    minWidth: 0,
    "& .player-name": {
      overflow: "hidden",
      textOverflow: "ellipsis",
      whiteSpace: "nowrap",
      color: selected ? theme.palette.primary.main : "inherit",
      cursor: "pointer",
      "&:hover": {
        textDecoration: "underline",
      },
    },
  },
  "& .level": {
    fontWeight: "bold",
    textAlign: "center",
    color: selected
      ? theme.palette.primary.main
      : level
      ? tierColors[getPlayerTier(level)]
      : "inherit",
  },
  [theme.breakpoints.down("sm")]: {
    gridTemplateColumns: gridTemplateColumns.sm,
    fontSize: "0.875rem",
  },
}));

const HeaderRow = styled(Box)(({ theme }) => ({
  display: "grid",
  gridTemplateColumns: gridTemplateColumns.default,
  padding: theme.spacing(0.5, 1),
  borderBottom: `1px solid ${theme.palette.divider}`,
  backgroundColor: theme.palette.background.default,
  position: "sticky",
  top: 0,
  zIndex: 1,
  "& > *": {
    textAlign: "right",
    color: theme.palette.text.secondary,
    fontSize: "0.75rem",
    fontWeight: "bold",
    whiteSpace: "nowrap",
  },
  "& > :nth-of-type(1)": {
    textAlign: "center",
  },
  "& > :nth-of-type(2)": {
    textAlign: "left",
  },
  [theme.breakpoints.down("sm")]: {
    gridTemplateColumns: gridTemplateColumns.sm,
    fontSize: "0.75rem",
  },
}));

const TeamHeaderRow = styled(Box)(({ theme }) => ({
  display: "grid",
  marginBottom: theme.spacing(1),
  gridTemplateColumns: gridTemplateColumns.default,
  padding: theme.spacing(0.5, 1),
  alignItems: "center",
  "& > *": {
    textAlign: "right",
    fontFamily: "Roboto Mono, monospace",
    whiteSpace: "nowrap",
    fontSize: "0.75rem",
    color: theme.palette.text.secondary,
    fontWeight: "bold",
  },
  "& > :nth-of-type(1)": {
    textAlign: "center",
    color: theme.palette.primary.main,
  },
  "& > :nth-of-type(2)": {
    textAlign: "left",
  },
  [theme.breakpoints.down("sm")]: {
    gridTemplateColumns: gridTemplateColumns.sm,
  },
}));

const CommanderRow = styled(Box)(({ theme, selected, level }) => ({
  display: "grid",
  gridTemplateColumns: gridTemplateColumns.default,
  padding: theme.spacing(2, 1),
  alignItems: "center",
  borderBottom: `1px solid ${theme.palette.divider}`,
  backgroundColor: theme.palette.background.paper,
  cursor: "pointer",
  "&:hover": {
    backgroundColor: selected
      ? theme.palette.action.selected
      : theme.palette.action.hover,
  },
  "& .stat": {
    textAlign: "right",
    fontFamily: "Roboto Mono, monospace",
    whiteSpace: "nowrap",
    color: selected ? theme.palette.primary.main : "inherit",
  },
  "& .player-info": {
    display: "flex",
    alignItems: "center",
    gap: theme.spacing(1),
    minWidth: 0,
    "& .player-name": {
      overflow: "hidden",
      textOverflow: "ellipsis",
      whiteSpace: "nowrap",
      color: selected ? theme.palette.primary.main : "inherit",
      cursor: "pointer",
      "&:hover": {
        textDecoration: "underline",
      },
    },
    "& .no-commander": {
      display: "flex",
      alignItems: "center",
      gap: theme.spacing(1),
      color: selected
        ? theme.palette.primary.contrastText
        : theme.palette.text.secondary,
      fontStyle: "italic",
    },
  },
  "& .level": {
    fontWeight: "bold",
    textAlign: "center",
    color: selected
      ? theme.palette.primary.main
      : level
      ? tierColors[getPlayerTier(level)]
      : "inherit",
  },
  [theme.breakpoints.down("sm")]: {
    gridTemplateColumns: gridTemplateColumns.sm,
    fontSize: "0.875rem",
  },
}));

const TeamSection = ({
  team,
  title,
  selectedPlayers,
  onTogglePlayer,
  onToggleSquad,
  onToggleAll,
  expandedSquads,
  onToggleExpand,
  onTeamExpand,
  onTeamCollapse,
}) => {
  const { openWithId } = usePlayerSidebar();

  const { commander, squadGroups, unassignedPlayers, allPlayers } =
    useMemo(() => {
      // Filter out command squad and sort remaining squads
      const squads = team.squads
        .filter((s) => s.name !== "command" && s.name !== UNASSIGNED)
        .sort((a, b) => a.name.localeCompare(b.name));

      // Group squads by type
      const grouped = squads.reduce((acc, squad) => {
        const type = squad.type || "infantry";
        if (!acc[type]) {
          acc[type] = [];
        }
        acc[type].push(squad);
        return acc;
      }, {});

      // Define the order of squad types
      const typeOrder = ["infantry", "armor", "recon"];
      const squadGroups = typeOrder.reduce((acc, type) => {
        if (grouped[type]?.length > 0) {
          acc.push({
            type,
            squads: grouped[type],
          });
        }
        return acc;
      }, []);

      const unassignedSquad = team.squads.find((s) => s.name === UNASSIGNED);

      // Create a list of all players for selection
      const allPlayers = [];
      if (team.commander) {
        allPlayers.push(team.commander);
      }
      squadGroups.forEach(({ squads }) => {
        squads.forEach((squad) => {
          allPlayers.push(...squad.players);
        });
      });
      allPlayers.push(...(unassignedSquad?.players || []));

      return {
        commander: team.commander,
        squadGroups,
        unassignedPlayers: unassignedSquad?.players || [],
        allPlayers,
      };
    }, [team]);

  const handleProfileClick = (player, event) => {
    event.stopPropagation();
    openWithId(player.player_id);
  };

  return (
    <TeamBox>
      <Box
        sx={{
          backgroundColor: (theme) => theme.palette.background.default,
          display: "flex",
          alignItems: "center",
          gap: 1,
          p: 1
        }}
      >
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <Checkbox
            size="small"
            checked={
              allPlayers.length > 0 &&
              allPlayers.every((p) => selectedPlayers.has(p.player_id))
            }
            indeterminate={
              allPlayers.some((p) => selectedPlayers.has(p.player_id)) &&
              !allPlayers.every((p) => selectedPlayers.has(p.player_id))
            }
            onChange={(e) => onToggleAll(allPlayers, e.target.checked)}
            sx={{
              color: (theme) => theme.palette.text.secondary,
              "&.Mui-checked, &.MuiCheckbox-indeterminate": {
                color: (theme) => theme.palette.primary.main,
              },
            }}
          />
          <Typography
            variant="body2"
            sx={{
              color: "text.secondary",
              minWidth: 100,
            }}
          >
            {!allPlayers.some((p) => selectedPlayers.has(p.player_id))
              ? "Select all"
              : allPlayers.every((p) => selectedPlayers.has(p.player_id))
              ? "All selected"
              : `${
                  allPlayers.filter((p) => selectedPlayers.has(p.player_id))
                    .length
                } selected`}
          </Typography>
        </Box>
        <Typography
          variant="h6"
          sx={{
            textTransform: "uppercase",
            fontWeight: "bold",
            flex: 1,
            textAlign: "center",
          }}
        >
          {title}
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <IconButton
            size="small"
            onClick={onTeamExpand}
          >
            <ExpandMoreIcon />
          </IconButton>
          <IconButton
            size="small"
            onClick={onTeamCollapse}
          >
            <ChevronRightIcon />
          </IconButton>
        </Box>
      </Box>
      <ScrollContainer>
        <ContentWrapper>
          <HeaderRow>
            <Box>LVL</Box>
            <Box>Name</Box>
            <Box>Kills</Box>
            <Box>Deaths</Box>
            <Box>Combat</Box>
            <Box>Offense</Box>
            <Box>Defense</Box>
            <Box>Support</Box>
          </HeaderRow>
          <TeamHeaderRow>
            <Box>∅ {team.avg_level.toFixed(0)}</Box>
            <Box style={{ textAlign: "center" }}>
              Total ({team.count} players)
            </Box>
            <Box>{team.kills}</Box>
            <Box>{team.deaths}</Box>
            <Box>{team.combat}</Box>
            <Box>{team.offense}</Box>
            <Box>{team.defense}</Box>
            <Box>{team.support}</Box>
          </TeamHeaderRow>
          <CommanderRow
            selected={commander && selectedPlayers.has(commander.player_id)}
            onClick={(e) => commander && onTogglePlayer(commander, e)}
            level={commander?.level}
          >
            <Box className="level">{commander?.level || "-"}</Box>
            <Box className="player-info">
              {commander ? (
                <>
                  <img
                    src="/icons/roles/armycommander.png"
                    alt="commander"
                    width={16}
                    height={16}
                  />
                  <Typography
                    className="player-name"
                    onClick={(e) => handleProfileClick(commander, e)}
                  >
                    {commander.name}
                  </Typography>
                  {commander.is_vip && <StarIcon sx={{ fontSize: 16 }} />}
                </>
              ) : (
                <Box className="no-commander">
                  <PersonOffIcon sx={{ fontSize: 16 }} />
                  <Typography>No Commander</Typography>
                </Box>
              )}
            </Box>
            <Box className="stat">{commander?.kills || 0}</Box>
            <Box className="stat">{commander?.deaths || 0}</Box>
            <Box className="stat">{commander?.combat || 0}</Box>
            <Box className="stat">{commander?.offense || 0}</Box>
            <Box className="stat">{commander?.defense || 0}</Box>
            <Box className="stat">{commander?.support || 0}</Box>
          </CommanderRow>
          {squadGroups.map(({ type, squads }) => (
            <Box key={type}>
              <Typography
                variant="subtitle2"
                sx={{
                  px: 1,
                  py: 0.5,
                  backgroundColor: (theme) => theme.palette.background.default,
                  color: (theme) => theme.palette.text.secondary,
                  borderBottom: (theme) => `1px solid ${theme.palette.divider}`,
                  textTransform: "uppercase",
                  display: "flex",
                  alignItems: "center",
                  gap: 1,
                }}
              >
                {type}
              </Typography>
              {squads.map((squad) => {
                return (
                  <Box key={squad.name}>
                    <SquadHeader
                      selected={squad.players.every((p) =>
                        selectedPlayers.has(p.player_id)
                      )}
                      onClick={(e) => onToggleSquad(squad.players, squad.players.every(p => selectedPlayers.has(p.player_id)))}
                    >
                      <Box className="squad-info">
                        <IconButton
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation();
                            onToggleExpand(squad.name);
                          }}
                        >
                          {expandedSquads[squad.name] ? (
                            <ExpandMoreIcon />
                          ) : (
                            <ChevronRightIcon />
                          )}
                        </IconButton>
                        <Box className="squad-name-container">
                          {squad.type && (
                            <img
                              src={`/icons/roles/${squad.type}.png`}
                              alt={squad.type}
                              width={16}
                              height={16}
                            />
                          )}
                          <Typography
                            variant="subtitle2"
                            sx={{
                              textTransform: "uppercase",
                              fontWeight: "bold",
                              minWidth: 0,
                              overflow: "hidden",
                              textOverflow: "ellipsis",
                            }}
                          >
                            {squad.name} ({squad.players.length})
                          </Typography>
                          {!squad.has_leader && (
                            <img
                              src="/icons/ping.webp"
                              alt="No Leader"
                              width={16}
                              height={16}
                              style={{ opacity: 0.7 }}
                            />
                          )}
                        </Box>
                        <Typography variant="caption" sx={{ ml: "auto" }}>
                          ∅{" "}
                          <Box
                            component="span"
                            sx={{
                              color: tierColors[getPlayerTier(squad.level)],
                            }}
                          >
                            {squad.level.toFixed(0)}
                          </Box>
                        </Typography>
                      </Box>
                      <Box className="squad-stats">
                        <Box className="stat">{squad.kills}</Box>
                        <Box className="stat">{squad.deaths}</Box>
                        <Box className="stat">{squad.combat}</Box>
                        <Box className="stat">{squad.offense}</Box>
                        <Box className="stat">{squad.defense}</Box>
                        <Box className="stat">{squad.support}</Box>
                      </Box>
                    </SquadHeader>
                    <Collapse in={expandedSquads[squad.name]}>
                      {squad.players.map((player) => (
                        <PlayerRow
                          key={player.player_id}
                          selected={selectedPlayers.has(player.player_id)}
                          onClick={(e) => onTogglePlayer(player, e)}
                          level={player.level}
                        >
                          <Box className="level">{player.level}</Box>
                          <Box className="player-info">
                            {player.role && (
                              <img
                                src={`/icons/roles/${player.role}.png`}
                                alt={player.role}
                                width={16}
                                height={16}
                              />
                            )}
                            <Typography
                              className="player-name"
                              onClick={(e) => handleProfileClick(player, e)}
                            >
                              {player.name}
                            </Typography>
                            {player.is_vip && (
                              <StarIcon sx={{ fontSize: 16 }} />
                            )}
                          </Box>
                          <Box className="stat">{player.kills}</Box>
                          <Box className="stat">{player.deaths}</Box>
                          <Box className="stat">{player.combat}</Box>
                          <Box className="stat">{player.offense}</Box>
                          <Box className="stat">{player.defense}</Box>
                          <Box className="stat">{player.support}</Box>
                        </PlayerRow>
                      ))}
                    </Collapse>
                  </Box>
                );
              })}
            </Box>
          ))}
          {unassignedPlayers.length > 0 && (
            <Box>
              <SquadHeader
                selected={unassignedPlayers.every((p) =>
                  selectedPlayers.has(p.player_id)
                )}
                onClick={(e) =>
                  onToggleSquad(unassignedPlayers, unassignedPlayers.every(p => selectedPlayers.has(p.player_id)))
                }
              >
                <Box className="squad-info">
                  <IconButton
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation();
                      onToggleExpand(UNASSIGNED);
                    }}
                  >
                    {expandedSquads[UNASSIGNED] ? (
                      <ExpandMoreIcon />
                    ) : (
                      <ChevronRightIcon />
                    )}
                  </IconButton>
                  <Box className="squad-name-container">
                    <Typography
                      variant="subtitle2"
                      sx={{
                        textTransform: "uppercase",
                        fontWeight: "bold",
                        minWidth: 0,
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                      }}
                    >
                      No Platoon ({unassignedPlayers.length})
                    </Typography>
                  </Box>
                </Box>
                <Box className="squad-stats">
                  <Box className="stat">
                    {unassignedPlayers.reduce((sum, p) => sum + p.kills, 0)}
                  </Box>
                  <Box className="stat">
                    {unassignedPlayers.reduce((sum, p) => sum + p.deaths, 0)}
                  </Box>
                  <Box className="stat">
                    {unassignedPlayers.reduce((sum, p) => sum + p.combat, 0)}
                  </Box>
                  <Box className="stat">
                    {unassignedPlayers.reduce((sum, p) => sum + p.offense, 0)}
                  </Box>
                  <Box className="stat">
                    {unassignedPlayers.reduce((sum, p) => sum + p.defense, 0)}
                  </Box>
                  <Box className="stat">
                    {unassignedPlayers.reduce((sum, p) => sum + p.support, 0)}
                  </Box>
                </Box>
              </SquadHeader>
              <Collapse in={expandedSquads[UNASSIGNED]}>
                {unassignedPlayers.map((player) => (
                  <PlayerRow
                    key={player.player_id}
                    selected={selectedPlayers.has(player.player_id)}
                    onClick={(e) => onTogglePlayer(player, e)}
                    level={player.level}
                  >
                    <Box className="level">{player.level}</Box>
                    <Box className="player-info">
                      <Typography
                        sx={{ width: 16, height: 16, textAlign: "center" }}
                      >
                        {"-"}
                      </Typography>
                      <Typography
                        className="player-name"
                        onClick={(e) => handleProfileClick(player, e)}
                      >
                        {player.name}
                      </Typography>
                      {player.is_vip && <StarIcon sx={{ fontSize: 16 }} />}
                    </Box>
                    <Box className="stat">{player.kills}</Box>
                    <Box className="stat">{player.deaths}</Box>
                    <Box className="stat">{player.combat}</Box>
                    <Box className="stat">{player.offense}</Box>
                    <Box className="stat">{player.defense}</Box>
                    <Box className="stat">{player.support}</Box>
                  </PlayerRow>
                ))}
              </Collapse>
            </Box>
          )}
        </ContentWrapper>
      </ScrollContainer>
    </TeamBox>
  );
};

const TeamViewPage = () => {
  const { data: teams, isFetching } = useQuery({
    ...teamsLiveQueryOptions,
    staleTime: 5 * 1000,
    refetchInterval: 10 * 1000,
  });

  const [selectedPlayers, setSelectedPlayers] = useState(new Map());
  const [expandedSquads, setExpandedSquads] = useState({
    allies: { [UNASSIGNED]: true },
    axis: { [UNASSIGNED]: true }
  });
  

  const { axisTeam, alliesTeam } = useMemo(() => {
    return {
      axisTeam: extractTeamState(teams?.axis),
      alliesTeam: extractTeamState(teams?.allies),
    };
  }, [teams]);

  // Get all squads from both teams
  const allSquads = useMemo(() => {
    const squads = {
      allies: new Set(),
      axis: new Set()
    };

    if (!alliesTeam || !axisTeam) return squads;
    
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
    
    return squads;
  }, [alliesTeam, axisTeam]);

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
    const newState = { allies: {}, axis: {} };
    Object.entries(allSquads).forEach(([team, squads]) => {
      squads.forEach(squadName => {
        newState[team][squadName] = true;
      });
      newState[team][UNASSIGNED] = true;
    });
    setExpandedSquads(newState);
  };

  const handleCollapseAll = () => {
    const newState = { allies: {}, axis: {} };
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
        <TeamSection
          team={alliesTeam}
          title="ALLIES"
          selectedPlayers={selectedPlayers}
          onTogglePlayer={handleTogglePlayer}
          onToggleSquad={handleToggleSquadSelection}
          onToggleAll={handleToggleTeam}
          expandedSquads={expandedSquads.allies}
          onToggleExpand={(squadName) => handleToggleSquad('allies', squadName)}
          onTeamExpand={() => handleTeamExpandAll('allies')}
          onTeamCollapse={() => handleTeamCollapseAll('allies')}
        />
        <TeamSection
          team={axisTeam}
          title="AXIS"
          selectedPlayers={selectedPlayers}
          onTogglePlayer={handleTogglePlayer}
          onToggleSquad={handleToggleSquadSelection}
          onToggleAll={handleToggleTeam}
          expandedSquads={expandedSquads.axis}
          onToggleExpand={(squadName) => handleToggleSquad('axis', squadName)}
          onTeamExpand={() => handleTeamExpandAll('axis')}
          onTeamCollapse={() => handleTeamCollapseAll('axis')}
        />
      </TeamContainer>
    </Stack>
  );
};

export default TeamViewPage;
