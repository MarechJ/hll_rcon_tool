import { useMemo } from "react";
import { getPlayerTier, useTierColors } from "@/utils/lib";
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
import UnfoldMoreIcon from "@mui/icons-material/UnfoldMore";
import UnfoldLessIcon from "@mui/icons-material/UnfoldLess";
import useTheme from "@mui/material/styles/useTheme";
import { secondsToTime } from "@/utils/extractPlayers";
import { ActionMenuButton } from "@/features/player-action/ActionMenu";
import { generatePlayerActions } from "@/features/player-action/actions";
import { TextButton } from "@/components/table/styles";

export const UNASSIGNED = "unassigned";

const PlayerStats = ({ player }) => (
  <>
    <Box className="stat">{player?.kills || 0}</Box>
    <Box className="stat">{player?.deaths || 0}</Box>
    <Box className="stat">{player?.combat || 0}</Box>
    <Box className="stat">{player?.offense || 0}</Box>
    <Box className="stat">{player?.defense || 0}</Box>
    <Box className="stat">{player?.support || 0}</Box>
    <Box className="stat">
      {secondsToTime(
        player?.time ?? player?.profile?.current_playtime_seconds ?? 0
      )}
    </Box>
  </>
);

const roleSrc = (role, mode) =>
  mode === "light"
    ? `/icons/roles/${role}_black.png`
    : `/icons/roles/${role}.png`;

const PlayerInfo = ({ player }) => {
  const theme = useTheme();
  const mode = theme?.palette?.mode || "light";
  return (
    <Box className="player-info">
      {player.role ? (
        <img
          src={roleSrc(player.role, mode)}
          alt={player.role}
          width={16}
          height={16}
          title={player.role}
        />
      ) : (
        <Typography sx={{ width: 16, height: 16, textAlign: "center" }}>
          {"-"}
        </Typography>
      )}
      <span onClick={(e) => e.stopPropagation()}>
        <ActionMenuButton
          actions={generatePlayerActions({
            multiAction: false,
            onlineAction: true,
          })}
          withProfile
          recipients={player}
          renderButton={(props) => (
            <TextButton {...props} className="player-name">
              {player.name}
            </TextButton>
          )}
        />
      </span>
      {player.is_vip && <StarIcon sx={{ fontSize: 16 }} />}
    </Box>
  );
};

const PlayerRowWrapper = ({
  player,
  selected,
  isCommander,
  onToggle,
  displayStats = true,
}) => (
  <PlayerRow
    selected={selected}
    onClick={(e) => onToggle(player, e)}
    level={player.level}
    isCommander={isCommander}
  >
    <Box className="level">{player.level}</Box>
    <PlayerInfo player={player} />
    {displayStats && <PlayerStats player={player} />}
  </PlayerRow>
);

const SquadPlayers = ({
  squad,
  collapsed,
  selectedPlayers,
  onTogglePlayer,
  displayStats = true,
}) => (
  <Collapse in={collapsed}>
    {squad.players.map((player) => (
      <PlayerRowWrapper
        key={player.player_id}
        player={player}
        selected={selectedPlayers.has(player.player_id)}
        onToggle={onTogglePlayer}
        displayStats={displayStats}
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
    <Box className="stat">∅ {secondsToTime(squad.time)}</Box>
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
    <Box className="stat"></Box>
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

const SquadNameInfo = ({ squad, showIcon = true }) => {
  const theme = useTheme();
  const mode = theme?.palette?.mode || "light";
  return (
    <Box className="squad-name-container">
      {showIcon && squad.type && (
        <img
          src={roleSrc(squad.type, mode)}
          alt={squad.type}
          width={16}
          height={16}
          title={squad.type}
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
          title="Unit has no leader"
          width={16}
          height={16}
          style={{ opacity: 0.7 }}
        />
      )}
    </Box>
  );
};

const SquadHeaderContent = ({ squad, collapsedSquads, onToggleExpand }) => {
  const tierColors = useTierColors();
  return (
    <Box className="squad-info">
      <IconButton
        size="small"
        onClick={(e) => {
          e.stopPropagation();
          onToggleExpand(squad.name);
        }}
      >
        {!collapsedSquads[squad.name] ? (
          <ExpandMoreIcon />
        ) : (
          <ChevronRightIcon />
        )}
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
          {squad.level}
        </Box>
      </Typography>
    </Box>
  );
};

export const TeamSection = ({
  team,
  title,
  selectedPlayers,
  onTogglePlayer,
  onToggleSquad,
  onToggleAll,
  collapsedSquads,
  onToggleExpand,
  onTeamExpand,
  onTeamCollapse,
}) => {
  const isLobby = team.name === "lobby";

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
      const typeOrder = ["infantry", "armor", "recon", "artillery"];
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
          onClick={(_) =>
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
              {!collapsedSquads[UNASSIGNED] ? (
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
                {isLobby ? "Lobby" : "No Platoon"} ({players.length})
              </Typography>
            </Box>
          </Box>
          <UnassignedStats players={players} />
        </SquadHeader>
        <SquadPlayers
          squad={{ players }}
          collapsed={!collapsedSquads[UNASSIGNED]}
          selectedPlayers={selectedPlayers}
          onTogglePlayer={onTogglePlayer}
        />
      </Box>
    );
  };

  const getLobbyPlayers = (players) => {
    if (players.length === 0) {
      return null;
    }
    return (
      <SquadPlayers
        squad={{ players }}
        collapsed={!collapsedSquads[UNASSIGNED]}
        selectedPlayers={selectedPlayers}
        onTogglePlayer={onTogglePlayer}
        displayStats={false}
      />
    );
  };

  const anySquadCollapsed = Object.values(collapsedSquads).some(Boolean);

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
          {isLobby ? `Lobby (${team.count})` : title}
        </Typography>
        <Box sx={{ display: "flex", gap: 1 }}>
          {anySquadCollapsed ? (
            <IconButton size="small" onClick={onTeamExpand}>
              <UnfoldMoreIcon />
            </IconButton>
          ) : (
            <IconButton size="small" onClick={onTeamCollapse}>
              <UnfoldLessIcon />
            </IconButton>
          )}
        </Box>
      </Box>
      <ScrollContainer>
        <ContentWrapper>
          {!isLobby ? (
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
                <Box>Time</Box>
              </HeaderRow>
              <TeamHeaderRow>
                <Box>∅ {team.avg_level}</Box>
                <Box style={{ textAlign: "center" }}>
                  Total ({team.count} players)
                </Box>
                <Box className="stat">{team?.kills || 0}</Box>
                <Box className="stat">{team?.deaths || 0}</Box>
                <Box className="stat">{team?.combat || 0}</Box>
                <Box className="stat">{team?.offense || 0}</Box>
                <Box className="stat">{team?.defense || 0}</Box>
                <Box className="stat">{team?.support || 0}</Box>
                <Box className="stat">∅ {secondsToTime(team?.time ?? 0)}</Box>
              </TeamHeaderRow>

              {commander ? (
                <PlayerRowWrapper
                  player={commander}
                  selected={selectedPlayers.has(commander.player_id)}
                  onToggle={onTogglePlayer}
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
                        onClick={(_) =>
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
                          collapsedSquads={collapsedSquads}
                          onToggleExpand={onToggleExpand}
                        />
                        <SquadStats squad={squad} />
                      </SquadHeader>
                      <SquadPlayers
                        squad={squad}
                        collapsed={!collapsedSquads[squad.name]}
                        selectedPlayers={selectedPlayers}
                        onTogglePlayer={onTogglePlayer}
                      />
                    </Box>
                  ))}
                </Box>
              ))}
            </>
          ) : (
            getLobbyPlayers(unassignedPlayers)
          )}
        </ContentWrapper>
      </ScrollContainer>
    </TeamBox>
  );
};
