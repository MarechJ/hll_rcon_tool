import { useState, useMemo } from "react";
import { extractPlayers, extractTeamState } from "@/utils/extractPlayers";
import { getPlayerTier, tierColors } from "@/utils/lib";
import teamViewResult from "./team-view.json";
import { Box, Typography, IconButton, Collapse } from "@mui/material";
import { styled } from "@mui/material/styles";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import PersonOffIcon from "@mui/icons-material/PersonOff";
import StarIcon from "@mui/icons-material/Star";

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

const SquadHeader = styled(Box)(({ theme }) => ({
  padding: theme.spacing(0.5, 1),
  backgroundColor: theme.palette.background.default,
  borderBottom: `1px solid ${theme.palette.divider}`,
  display: "grid",
  gridTemplateColumns: gridTemplateColumns.default,
  alignItems: "center",
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
    },
  },
  "& .squad-stats": {
    display: "contents",
    "& .stat": {
      textAlign: "right",
      fontFamily: "Roboto Mono, monospace",
      whiteSpace: "nowrap",
      fontSize: "0.75rem",
      color: theme.palette.text.secondary,
    },
  },
  [theme.breakpoints.down("sm")]: {
    gridTemplateColumns: gridTemplateColumns.sm,
  },
}));

const PlayerRow = styled(Box)(({ theme }) => ({
  display: "grid",
  gridTemplateColumns: gridTemplateColumns.default,
  padding: theme.spacing(0.5, 1),
  alignItems: "center",
  borderBottom: `1px solid ${theme.palette.divider}`,
  backgroundColor: theme.palette.background.paper,
  "&:hover": {
    backgroundColor: theme.palette.action.hover,
  },
  "& .stat": {
    textAlign: "right",
    fontFamily: "Roboto Mono, monospace",
    whiteSpace: "nowrap",
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
    },
  },
  "& .level": {
    fontWeight: "bold",
    textAlign: "center",
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

const CommanderRow = styled(Box)(({ theme }) => ({
  display: "grid",
  gridTemplateColumns: gridTemplateColumns.default,
  padding: theme.spacing(2, 1),
  alignItems: "center",
  borderBottom: `1px solid ${theme.palette.divider}`,
  backgroundColor: theme.palette.background.paper,
  "& .stat": {
    textAlign: "right",
    fontFamily: "Roboto Mono, monospace",
    whiteSpace: "nowrap",
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
    },
    "& .no-commander": {
      display: "flex",
      alignItems: "center",
      gap: theme.spacing(1),
      color: theme.palette.text.secondary,
      fontStyle: "italic",
    },
  },
  "& .level": {
    fontWeight: "bold",
    textAlign: "center",
  },
  [theme.breakpoints.down("sm")]: {
    gridTemplateColumns: gridTemplateColumns.sm,
    fontSize: "0.875rem",
  },
}));

const TeamSection = ({ team, title }) => {
  const [expandedSquads, setExpandedSquads] = useState({ [UNASSIGNED]: true });

  const { commander, squadGroups, unassignedPlayers } = useMemo(() => {
    // Filter out command squad and sort remaining squads
    const squads = team.squads
      .filter((s) => s.name !== "command" && s.name !== UNASSIGNED)
      .sort((a, b) => a.name.localeCompare(b.name));

    // Group squads by type
    const grouped = squads.reduce((acc, squad) => {
      const type = squad.type || 'infantry';
      if (!acc[type]) {
        acc[type] = [];
      }
      acc[type].push(squad);
      return acc;
    }, {});

    // Define the order of squad types
    const typeOrder = ['infantry', 'armor', 'recon'];
    const squadGroups = typeOrder.reduce((acc, type) => {
      if (grouped[type]?.length > 0) {
        acc.push({
          type,
          squads: grouped[type]
        });
      }
      return acc;
    }, []);

    const unassignedSquad = team.squads.find((s) => s.name === UNASSIGNED);

    return {
      commander: team.commander,
      squadGroups,
      unassignedPlayers: unassignedSquad?.players || [],
    };
  }, [team]);

  const toggleSquad = (squadName) => {
    setExpandedSquads((prev) => ({
      ...prev,
      [squadName]: !prev[squadName],
    }));
  };

  const toggleAll = (expanded) => {
    const allSquads = {};
    squadGroups.forEach(({ squads }) => {
      squads.forEach((squad) => {
        allSquads[squad.name] = expanded;
      });
    });
    if (unassignedPlayers.length > 0) {
      allSquads[UNASSIGNED] = expanded;
    }
    setExpandedSquads(allSquads);
  };

  return (
    <TeamBox>
      <Box
        sx={{
          p: 1,
          backgroundColor: (theme) => theme.palette.background.default,
          display: "flex",
          alignItems: "center",
          gap: 1,
        }}
      >
        <Typography
          variant="h6"
          sx={{
            textTransform: "uppercase",
            fontWeight: "bold",
            flex: 1,
          }}
        >
          {title}
        </Typography>
        <IconButton
          aria-label="Expand all"
          size="small"
          onClick={() => toggleAll(true)}
          sx={{ color: (theme) => theme.palette.text.secondary }}
        >
          <ExpandMoreIcon />
        </IconButton>
        <IconButton
          aria-label="Collapse all"
          size="small"
          onClick={() => toggleAll(false)}
          sx={{ color: (theme) => theme.palette.text.secondary }}
        >
          <ChevronRightIcon />
        </IconButton>
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
          <CommanderRow>
            <Box
              className="level"
              sx={{
                color: commander
                  ? tierColors[getPlayerTier(commander.level)]
                  : "inherit",
              }}
            >
              {commander?.level || "-"}
            </Box>
            <Box className="player-info">
              {commander ? (
                <>
                  <img
                    src="/icons/roles/armycommander.png"
                    alt="commander"
                    width={16}
                    height={16}
                  />
                  <Typography className="player-name">
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
                  textTransform: 'uppercase',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                }}
              >
                {type}
              </Typography>
              {squads.map((squad) => {
                return (
                  <Box key={squad.name}>
                    <SquadHeader>
                      <Box className="squad-info">
                        <IconButton
                          size="small"
                          onClick={() => toggleSquad(squad.name)}
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
                            sx={{ color: tierColors[getPlayerTier(squad.level)] }}
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
                        <PlayerRow key={player.player_id}>
                          <Box
                            className="level"
                            sx={{ color: tierColors[getPlayerTier(player.level)] }}
                          >
                            {player.level}
                          </Box>
                          <Box className="player-info">
                            {player.role && (
                              <img
                                src={`/icons/roles/${player.role}.png`}
                                alt={player.role}
                                width={16}
                                height={16}
                              />
                            )}
                            <Typography className="player-name">
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
                );
              })}
            </Box>
          ))}
          {unassignedPlayers.length > 0 && (
            <Box>
              <SquadHeader>
                <Box className="squad-info">
                  <IconButton
                    size="small"
                    onClick={() => toggleSquad(UNASSIGNED)}
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
                  <PlayerRow key={player.player_id}>
                    <Box
                      className="level"
                      sx={{ color: tierColors[getPlayerTier(player.level)] }}
                    >
                      {player.level}
                    </Box>
                    <Box className="player-info">
                      <Typography
                        sx={{ width: 16, height: 16, textAlign: "center" }}
                      >
                        {"-"}
                      </Typography>
                      <Typography className="player-name">
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
  const { axisTeam, alliesTeam, noneTeam } = useMemo(() => {
    return {
      axisTeam: extractTeamState(teamViewResult?.axis),
      alliesTeam: extractTeamState(teamViewResult?.allies),
      noneTeam: extractTeamState(teamViewResult?.none),
    };
  }, []);

  console.log(axisTeam, alliesTeam, noneTeam);

  return (
    <TeamContainer>
      <TeamSection team={alliesTeam} title="ALLIES" />
      <TeamSection team={axisTeam} title="AXIS" />
      {/* {noneTeam?.squads?.length > 0 && (
        <TeamSection team={noneTeam} title="UNDECIDED" />
      )} */}
    </TeamContainer>
  );
};

export default TeamViewPage;
