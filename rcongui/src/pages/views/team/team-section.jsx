import { useMemo } from "react";
import { usePlayerSidebar } from "@/hooks/usePlayerSidebar";
import { getPlayerTier, tierColors } from "@/utils/lib";
import StarIcon from "@mui/icons-material/Star";
import {
  TeamBox,
  ScrollContainer,
  ContentWrapper,
  HeaderRow,
  TeamHeaderRow,
  CommanderRow,
  PlayerRow,
  SquadHeader,
} from "./styled";
import { Box, Typography, IconButton, Checkbox } from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import PersonOffIcon from "@mui/icons-material/PersonOff";
import Collapse from "@mui/material/Collapse";

export const UNASSIGNED = "null";

const PlayerStats = ({ player }) => (
  <>
    <Box className="stat">{player?.kills || 0}</Box>
    <Box className="stat">{player?.deaths || 0}</Box>
    <Box className="stat">{player?.combat || 0}</Box>
    <Box className="stat">{player?.offense || 0}</Box>
    <Box className="stat">{player?.defense || 0}</Box>
    <Box className="stat">{player?.support || 0}</Box>
  </>
);

const PlayerInfo = ({ player, onProfileClick }) => (
  <Box className="player-info">
    {player.role ? (
      <img
        src={`/icons/roles/${player.role}.png`}
        alt={player.role}
        width={16}
        height={16}
      />
    ) : (
      <Typography sx={{ width: 16, height: 16, textAlign: "center" }}>
        {"-"}
      </Typography>
    )}
    <Typography
      className="player-name"
      onClick={(e) => onProfileClick(player, e)}
    >
      {player.name}
    </Typography>
    {player.is_vip && <StarIcon sx={{ fontSize: 16 }} />}
  </Box>
);

const PlayerRowWrapper = ({
  player,
  selected,
  isCommander,
  onToggle,
  onProfileClick,
}) => (
  <PlayerRow
    selected={selected}
    onClick={(e) => onToggle(player, e)}
    level={player.level}
    isCommander={isCommander}
  >
    <Box className="level">{player.level}</Box>
    <PlayerInfo player={player} onProfileClick={onProfileClick} />
    <PlayerStats player={player} />
  </PlayerRow>
);

const SquadPlayers = ({
  squad,
  expanded,
  selectedPlayers,
  onTogglePlayer,
  onProfileClick,
}) => (
  <Collapse in={expanded}>
    {squad.players.map((player) => (
      <PlayerRowWrapper
        key={player.player_id}
        player={player}
        selected={selectedPlayers.has(player.player_id)}
        onToggle={onTogglePlayer}
        onProfileClick={onProfileClick}
      />
    ))}
  </Collapse>
);

const SquadStats = ({ squad }) => (
  <Box className="squad-stats">
    <Box className="stat">{squad.kills}</Box>
    <Box className="stat">{squad.deaths}</Box>
    <Box className="stat">{squad.combat}</Box>
    <Box className="stat">{squad.offense}</Box>
    <Box className="stat">{squad.defense}</Box>
    <Box className="stat">{squad.support}</Box>
  </Box>
);

const UnassignedStats = ({ players }) => (
  <Box className="squad-stats">
    <Box className="stat">{players.reduce((sum, p) => sum + p.kills, 0)}</Box>
    <Box className="stat">{players.reduce((sum, p) => sum + p.deaths, 0)}</Box>
    <Box className="stat">{players.reduce((sum, p) => sum + p.combat, 0)}</Box>
    <Box className="stat">{players.reduce((sum, p) => sum + p.offense, 0)}</Box>
    <Box className="stat">{players.reduce((sum, p) => sum + p.defense, 0)}</Box>
    <Box className="stat">{players.reduce((sum, p) => sum + p.support, 0)}</Box>
  </Box>
);

const SquadGroupHeader = ({ type }) => (
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
);

const SquadNameInfo = ({ squad, showIcon = true }) => (
  <Box className="squad-name-container">
    {showIcon && squad.type && (
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
);

const SquadHeaderContent = ({ squad, expandedSquads, onToggleExpand }) => (
  <Box className="squad-info">
    <IconButton
      size="small"
      onClick={(e) => {
        e.stopPropagation();
        onToggleExpand(squad.name);
      }}
    >
      {expandedSquads[squad.name] ? <ExpandMoreIcon /> : <ChevronRightIcon />}
    </IconButton>
    <SquadNameInfo squad={squad} />
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
);

export const TeamSection = ({
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

  const handleProfileClick = (player, event) => {
    event.stopPropagation();
    openWithId(player.player_id);
  };

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

  const getUnassignedSquad = (players) => {
    if (players.length === 0) {
      return null;
    }
    return (
      <Box>
        <SquadHeader
          selected={players.every((p) => selectedPlayers.has(p.player_id))}
          onClick={(e) =>
            onToggleSquad(
              players,
              players.every((p) => selectedPlayers.has(p.player_id))
            )
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
                {team.name === "lobby" ? "Lobby" : "No Platoon"} (
                {players.length})
              </Typography>
            </Box>
          </Box>
          <UnassignedStats players={players} />
        </SquadHeader>
        <SquadPlayers
          squad={{ players }}
          expanded={expandedSquads[UNASSIGNED]}
          selectedPlayers={selectedPlayers}
          onTogglePlayer={onTogglePlayer}
          onProfileClick={handleProfileClick}
        />
      </Box>
    );
  };

  return (
    <TeamBox>
      <Box
        sx={{
          backgroundColor: (theme) => theme.palette.background.paper,
          display: "flex",
          alignItems: "center",
          gap: 1,
          p: 1,
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
        <Box sx={{ display: "flex", gap: 1 }}>
          <IconButton size="small" onClick={onTeamExpand}>
            <ExpandMoreIcon />
          </IconButton>
          <IconButton size="small" onClick={onTeamCollapse}>
            <ChevronRightIcon />
          </IconButton>
        </Box>
      </Box>
      <ScrollContainer>
        <ContentWrapper>
          {team.name !== "lobby" ? (
            <>
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
                <PlayerStats player={team} />
              </TeamHeaderRow>

              {commander ? (
                <PlayerRowWrapper
                  player={commander}
                  selected={selectedPlayers.has(commander.player_id)}
                  onToggle={onTogglePlayer}
                  onProfileClick={handleProfileClick}
                  isCommander={true}
                />
              ) : team.name !== "lobby" ? (
                <CommanderRow>
                  <Box className="level">-</Box>
                  <Box className="player-info">
                    <Box className="no-commander">
                      <PersonOffIcon sx={{ fontSize: 16 }} />
                      <Typography>No Commander</Typography>
                    </Box>
                  </Box>
                  <PlayerStats player={{}} />
                </CommanderRow>
              ) : null}

              {getUnassignedSquad(unassignedPlayers)}

              {squadGroups.map(({ type, squads }) => (
                <Box key={type}>
                  <SquadGroupHeader type={type} />
                  {squads.map((squad) => (
                    <Box key={squad.name}>
                      <SquadHeader
                        selected={squad.players.every((p) =>
                          selectedPlayers.has(p.player_id)
                        )}
                        onClick={(e) =>
                          onToggleSquad(
                            squad.players,
                            squad.players.every((p) =>
                              selectedPlayers.has(p.player_id)
                            )
                          )
                        }
                      >
                        <SquadHeaderContent
                          squad={squad}
                          expandedSquads={expandedSquads}
                          onToggleExpand={onToggleExpand}
                        />
                        <SquadStats squad={squad} />
                      </SquadHeader>
                      <SquadPlayers
                        squad={squad}
                        expanded={expandedSquads[squad.name]}
                        selectedPlayers={selectedPlayers}
                        onTogglePlayer={onTogglePlayer}
                        onProfileClick={handleProfileClick}
                      />
                    </Box>
                  ))}
                </Box>
              ))}
            </>
          ) : (
            getUnassignedSquad(unassignedPlayers)
          )}
        </ContentWrapper>
      </ScrollContainer>
    </TeamBox>
  );
};
