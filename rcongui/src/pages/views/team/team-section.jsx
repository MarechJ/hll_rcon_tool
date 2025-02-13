import { useMemo } from "react";
import { usePlayerSidebar } from "@/features/player-sidebar/hooks";
import { getPlayerTier } from "@/utils/player-utils";
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

export const UNASSIGNED = "null";

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
                      onClick={(e) =>
                        onToggleSquad(
                          squad.players,
                          squad.players.every((p) =>
                            selectedPlayers.has(p.player_id)
                          )
                        )
                      }
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
                  onToggleSquad(
                    unassignedPlayers,
                    unassignedPlayers.every((p) =>
                      selectedPlayers.has(p.player_id)
                    )
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
