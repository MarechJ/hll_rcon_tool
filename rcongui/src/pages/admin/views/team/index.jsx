import React, { Fragment } from "react";
import {
  Link,
  Modal,
  Typography,
  TextField,
  Avatar,
  ListItemSecondaryAction,
  Checkbox,
  LinearProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from "@mui/material";
import Grid from "@mui/material/Grid2";
import Autocomplete from '@mui/material/Autocomplete';
import WarningIcon from "@mui/icons-material/Warning";
import { fromJS, Map, List as IList, OrderedSet } from "immutable";
import ListSubheader from "@mui/material/ListSubheader";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import Collapse from "@mui/material/Collapse";
import { PlayerItem, KDChips, ScoreChips } from "@/components/PlayerView/playerList";
import {
  addPlayerToBlacklist,
  get,
  getBlacklists,
  handle_http_errors,
  postData,
  showResponse,
} from "@/utils/fetchUtils";
import {
  Duration,
  PlayerActions,
  ReasonDialog,
} from "@/components/PlayerView/playerActions";
import { toast } from "react-toastify";
import { FlagDialog } from "@/pages/admin/records/players";
import Padlock from "@/components/shared/Padlock";
import BlacklistRecordCreateDialog from "@/components/Blacklist/BlacklistRecordCreateDialog";

const Squad = ({
  squadName,
  squadData,
  doOpen,
  onSelectSquad,
  onSelectPlayer,
  selectedPlayers,
  selectMultiplePlayers,
  showOnlySelected,
}) => {
  const [open, setOpen] = React.useState(false);
  const handleClick = () => {
    setOpen(!open);
  };
  const sizes = {
    armor: 3,
    infantry: 6,
    recon: 2,
  };

  const squadPlayerNames = React.useMemo(
    () =>
      squadData.get("players", new IList()).map((player) => player.get("name")),
    [squadData]
  );

  const hasSelectedPlayers = React.useMemo(() => {
    const intersection = new OrderedSet(squadPlayerNames).intersect(
      selectedPlayers
    );
    return intersection.size !== 0;
  }, [selectedPlayers, squadPlayerNames]);

  const shouldHide = React.useMemo(
    () => showOnlySelected && !hasSelectedPlayers,
    [showOnlySelected, hasSelectedPlayers]
  );

  const deleteFlag = (flag_id) => {
    return postData(`${process.env.REACT_APP_API_URL}unflag_player`, {
      flag_id: flag_id,
    })
      .then((response) =>
        showResponse(response, "Flag will be removed momentarily", true)
      )
      .catch((error) => toast.error("Unable to connect to API " + error));
  };

  if (squadName === "commander") return "";

  return squadData && !shouldHide ? (
    <Fragment>
      <ListItem button onClick={handleClick}>
        <ListItemIcon>
          <Avatar
            variant="rounded"
            alt={squadData.get("type", "na")}
            src={
              squadName.toUpperCase() === "NULL"
                ? `icons/sleep.png`
                : `icons/roles/${squadData.get("type")}.png`
            }
          >
            {squadName[0].toUpperCase()}
          </Avatar>
        </ListItemIcon>
        <ListItemText
          primary={
            <Typography variant="h6">
              {`${squadName.toUpperCase() === "NULL"
                ? "Unassigned"
                : squadName.toUpperCase()
                } - ${squadData.get("players", new IList()).size}/${sizes[squadData.get("type", "infantry")]
                }`}{" "}
              {squadData.get("has_leader", false) ? (
                ""
              ) : (
                <WarningIcon
                  style={{ verticalAlign: "middle" }}
                  fontSize="small"
                  color="error"
                />
              )}
            </Typography>
          }
          secondary={
            <Grid container spacing={1}>
              <ScoreChips
                player={squadData}
              />
              <KDChips  player={squadData} />
            </Grid>
          }
        />

        <ListItemSecondaryAction>
          <Checkbox
            checked={selectedPlayers.isSuperset(squadPlayerNames)}
            onChange={() => {
              if (selectedPlayers.isSuperset(squadPlayerNames)) {
                selectMultiplePlayers(squadPlayerNames, "delete");
              } else {
                selectMultiplePlayers(squadPlayerNames, "add");
              }
            }}
          />
        </ListItemSecondaryAction>
      </ListItem>
      <Collapse
        in={open || doOpen || hasSelectedPlayers}
        timeout="auto"
        unmountOnExit
      >
        <List component="div" disablePadding >
          {squadData.get("players", new IList()).map((player) => {
            if (
              showOnlySelected &&
              !selectedPlayers.includes(player.get("name"))
            )
              return "";

            return (
              <PlayerItem
                key={player.get("name")}
                player={player}
                playerHasExtraInfo={true}
                onDeleteFlag={(flagId) => deleteFlag(flagId)}
                onSelect={() => onSelectPlayer(player.get("name"))}
                isSelected={selectedPlayers?.contains(player.get("name"))}
              />
            );
          })}
        </List>
      </Collapse>
    </Fragment>
  ) : (
    ""
  );
};

const Team = ({
  teamName,
  teamData,
  selectedPlayers,
  selectPlayer,
  selectMultiplePlayers,
  selectAll,
  deselectAll,
  sortFunc,
  showOnlySelected,
}) => {
  const [openAll, setOpenAll] = React.useState(false);

  const onOpenAll = () => (openAll ? setOpenAll(false) : setOpenAll(true));

  return teamData ? (
    <List
      dense
      component="nav"
      subheader={
        <ListSubheader component="div" id="nested-list-subheader">
          <Grid
            container
            alignContent="space-between"
            alignItems="flex-end"
            justifyContent="space-between"
            spacing={2}
          >
            <Grid size={9}>
              <Typography variant="h4" align="left">
                {teamName} {teamData.get("count", 0)}/50{" "}
                <Link onClick={onOpenAll} component="button">
                  {openAll ? "Collapse" : "Expand"} all
                </Link>{" "}
                <Link onClick={selectAll} component="button">
                  Select all
                </Link>{" "}
                <Link onClick={deselectAll} component="button">
                  Deselect all
                </Link>
              </Typography>
            </Grid>
          </Grid>
        </ListSubheader>
      }
    >
      {teamData.get("commander") &&
        (!showOnlySelected ||
          (showOnlySelected &&
            selectedPlayers.contains(teamData.get("commander")?.get("name")))) ? (
        <PlayerItem
          player={teamData.get("commander")}
          playerHasExtraInfo={true}
          onDeleteFlag={() => null}
          onSelect={() => selectPlayer(teamData.get("commander")?.get("name"))}
          isSelected={selectedPlayers?.contains(
            teamData.get("commander")?.get("name")
          )}
        />
      ) : (
        ""
      )}
      {teamData
        .get("squads", new Map())
        .toOrderedMap()
        .sortBy(sortFunc)
        .entrySeq()
        .map(([key, value]) => (
          <Squad
            key={key}
            squadName={key}
            squadData={value}
            doOpen={openAll}
            onSelectSquad={() => true}
            onSelectPlayer={selectPlayer}
            selectedPlayers={selectedPlayers}
            selectMultiplePlayers={selectMultiplePlayers}
            showOnlySelected={showOnlySelected}
          />
        ))}
    </List>
  ) : (
    ""
  );
};

const SimplePlayerRenderer = ({ player, flag }) => (
  <Typography variant="h4">
    Add {!flag ? "<select a flag>" : flag} to all selected players
  </Typography>
);

const GameView = () => {
  const [isLoading, setIsLoading] = React.useState(false);
  const [teamView, setTeamView] = React.useState(null);
  const [selectedPlayers, setSelectedPlayers] = React.useState(
    new OrderedSet()
  );
  const [refreshFreqSecs, setResfreshFreqSecs] = React.useState(5);
  const intervalHandleRef = React.useRef(null);
  const [flag, setFlag] = React.useState(false);
  const [blacklistDialogOpen, setBlacklistDialogOpen] = React.useState(false);
  const [blacklists, setBlacklists] = React.useState([]);
  const [sortType, setSortType] = React.useState(
    localStorage.getItem("game_view_sorting")
      ? localStorage.getItem("game_view_sorting")
      : "name_asc"
  );
  /* confirm action needs to be set to a dict to call the popup:
        {
          player: null,
          actionType: actionType,
          player_id: null,
        }
  */
  const [confirmAction, setConfirmAction] = React.useState(false);
  const [showOnlySelected, setShowOnlySelected] = React.useState(false);

  const sortTypeToFunc = React.useMemo(
    () => ({
      combat_desc: (squadData, squadName) => -squadData.get("combat", 0),
      offense_desc: (squadData, squadName) => -squadData.get("offense", 0),
      defense_desc: (squadData, squadName) => -squadData.get("defense", 0),
      support_desc: (squadData, squadName) => -squadData.get("support", 0),
      kills_desc: (squadData, squadName) => -squadData.get("kills", 0),
      deaths_desc: (squadData, squadName) => -squadData.get("kills", 0),
      name_asc: (squadData, squadName) => squadName,
      combat_asc: (squadData, squadName) => squadData.get("combat", 0),
      offense_asc: (squadData, squadName) => squadData.get("offense", 0),
      defense_asc: (squadData, squadName) => squadData.get("defense", 0),
      support_asc: (squadData, squadName) => squadData.get("support", 0),
      kills_asc: (squadData, squadName) => squadData.get("kills", 0),
      deaths_asc: (squadData, squadName) => squadData.get("kills", 0),
    }),
    []
  );

  const playerNamesToPlayerId = React.useMemo(() => {
    if (!teamView) {
      return new Map();
    }

    const namesToId = {};
    ["axis", "allies", "none"].forEach((key) => {
      teamView
        .get(key, new Map())
        .get("squads", new Map())
        .entrySeq()
        .forEach(([key, value]) =>
          value.get("players", new IList()).forEach((player) => {
            namesToId[player.get("name")] = player.get("player_id");
          })
        );

      const commander = teamView
        .get(key, new Map())
        .get("commander", new Map());
      if (commander) {
        namesToId[commander.get("name")] = commander.get("player_id");
      }
    });
    return fromJS(namesToId);
  }, [teamView]);

  const getPlayersNamesByTeam = (teamView, teamName) => {
    const commander = teamView
      .get(teamName, new Map())
      .get("commander", new Map())
      ?.get("name");

    const names = teamView
      .get(teamName, new Map())
      .get("squads", new Map())
      .entrySeq()
      .map(([key, value]) =>
        value.get("players", new IList()).map((player) => player.get("name"))
      )
      .flatten()
      .toList();

    if (commander) return names.push(commander);

    return names;
  };

  const autoCompleteSelectedPlayers = React.useMemo(
    () => selectedPlayers.toJS(),
    [selectedPlayers]
  );

  const allPlayerNames = React.useMemo(() => {
    if (!teamView) {
      return [];
    }

    const res = new IList(["axis", "allies", "none"])
      .map((key) => {
        return getPlayersNamesByTeam(teamView, key);
      })
      .flatten()
      .toJS();

    return res;
  }, [teamView]);

  const selectAllTeam = (teamName) => {
    selectMultiplePlayers(getPlayersNamesByTeam(teamView, teamName), "add");
  };

  const deselectAllTeam = (teamName) => {
    selectMultiplePlayers(getPlayersNamesByTeam(teamView, teamName), "delete");
  };

  const selectPlayer = (playerName, force) => {
    if (
      force !== "add" &&
      (selectedPlayers.includes(playerName) || force === "delete")
    ) {
      setSelectedPlayers(selectedPlayers.delete(playerName));
    } else if (
      force !== "delete" &&
      (!selectedPlayers.includes(playerName) || force === "add")
    ) {
      setSelectedPlayers(selectedPlayers.add(playerName));
    }
  };

  const selectMultiplePlayers = (playerNames, force) => {
    let newSelectedPlayer = selectedPlayers;

    playerNames.forEach((playerName) => {
      if (
        force !== "add" &&
        (selectedPlayers.includes(playerName) || force === "delete")
      ) {
        newSelectedPlayer = newSelectedPlayer.delete(playerName);
      } else if (
        force !== "delete" &&
        (!selectedPlayers.includes(playerName) || force === "add")
      ) {
        newSelectedPlayer = newSelectedPlayer.add(playerName);
      }
    });

    setSelectedPlayers(newSelectedPlayer);
  };

  const loadData = () => {
    setIsLoading(true);
    return get("get_team_view")
      .then((response) => showResponse(response, "get_team_view"))
      .then((data) => {
        setIsLoading(false);
        if (data.result) {
          setTeamView(fromJS(data.result));
        }
      })
      .catch(handle_http_errors);
  };

  React.useEffect(() => {
    loadData();
  }, []);

  React.useEffect(() => {
    // Set up the interval
    intervalHandleRef.current = setInterval(() => {
      loadData().catch(e => console.warn("Error in periodic refresh", e));
    }, refreshFreqSecs * 1000);

    // Clear the interval on component unmount or when refreshFreqSecs changes
    return () => {
      if (intervalHandleRef.current) {
        clearInterval(intervalHandleRef.current);
      }
    };
  }, [refreshFreqSecs]);

  const isMessageLessAction = (actionType) =>
    actionType.startsWith("switch_") || actionType.startsWith("unwatch_");

  const handleAction = (
    actionType,
    playerNames,
    message,
    duration_hours = 2,
    comment = null
  ) => {
    if (!message && !isMessageLessAction(actionType)) {
      setConfirmAction({
        player_name: null,
        actionType: actionType,
        player_id: null,
      });
    } else {
      playerNames.forEach((playerName) => {
        if (allPlayerNames.indexOf(playerName) === -1) {
          toast.error(`Player ${playerName} is not on the server anymore`);
          selectPlayer(playerName, "delete");
          return;
        }
        const player_id = playerNamesToPlayerId.get(playerName, null);
        const data = {
          player_name: playerName,
          player_id: player_id,
          reason: message,
          comment: comment,
          duration_hours: duration_hours,
          message: message,
        };

        postData(`${process.env.REACT_APP_API_URL}${actionType}`, data)
          .then((response) =>
            showResponse(response, `${actionType} ${playerName}`, true)
          )
          .catch(handle_http_errors);

        if (comment) {
          postData(`${process.env.REACT_APP_API_URL}post_player_comment`, {
            player_id: player_id,
            comment: comment,
          })
            .then((response) =>
              showResponse(response, `post_player_comment ${playerName}`, true)
            )
            .catch(handle_http_errors);
        }
      });
    }
  };

  const addFlagToPlayers = (_, flag, comment) => {
    selectedPlayers.forEach((name) =>
      postData(`${process.env.REACT_APP_API_URL}flag_player`, {
        player_id: playerNamesToPlayerId.get(name),
        flag: flag,
        comment: comment,
      })
        .then((response) => showResponse(response, "flag_player", true))
        .then(() => setFlag(false))
        .catch(handle_http_errors)
    );
  };

  function blacklistManyPlayers(payload) {
    const playersToBlacklist = selectedPlayers
    .toJS()
    .map(playerName => playerNamesToPlayerId.get(playerName))
    .filter(p => p !== undefined)

    Promise.allSettled(playersToBlacklist.map((playerId) => (
      addPlayerToBlacklist({
        ...payload,
        playerId,
      })
    )))

  }

  async function handleBlacklistOpen(player) {
    const blacklists = await getBlacklists();
    if (blacklists) {
      setBlacklists(blacklists);
      setBlacklistDialogOpen(true)
    }
  }

  function selectedPlayersToRows() {
    return selectedPlayers
    .toJS()
    .filter(p => playerNamesToPlayerId.get(p) !== undefined)
    .map(player => {
      const id = playerNamesToPlayerId.get(player)
      return `${player} -> ${id}`
    }).join(",\n")
  }

  return (
    (<Grid container spacing={2}>
      {teamView ? (
        <Fragment>
          <Grid size={12}>
            <LinearProgress
              style={{ visibility: isLoading ? "visible" : "hidden" }}
            />
          </Grid>
          <FlagDialog
            open={flag}
            handleClose={() => setFlag(false)}
            handleConfirm={addFlagToPlayers}
            SummaryRenderer={SimplePlayerRenderer}
          />
          <BlacklistRecordCreateDialog
            open={blacklistDialogOpen}
            blacklists={blacklists}
            initialValues={selectedPlayers && { playerId: selectedPlayersToRows() }}
            onSubmit={blacklistManyPlayers}
            setOpen={() => setBlacklistDialogOpen(false)}
            disablePlayerId={true}
            hasManyIDs={true}
          />
          <ReasonDialog
            open={confirmAction}
            handleClose={() => setConfirmAction(false)}
            handleConfirm={(
              action,
              player,
              reason,
              comment,
              duration_hours = 2,
              player_id = null
            ) => {
              handleAction(
                action,
                selectedPlayers,
                reason,
                duration_hours,
                comment
              );
              setConfirmAction(false);
            }}
          />
          <Grid size={12}>
            <Grid
              container
              alignItems="center"
              justifyContent="space-between"
              spacing={2}
            >
              <Grid size={12}>
                <Autocomplete
                  multiple
                  clearOnEscape
                  id="tags-outlined"
                  options={allPlayerNames.sort((a, b) => a.localeCompare(b))}
                  value={autoCompleteSelectedPlayers}
                  filterSelectedOptions
                  onChange={(e, val) => {
                    setSelectedPlayers(new OrderedSet(val));
                  }}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      variant="outlined"
                      label="Selected players to search or apply action to"
                      fullWidth
                    />
                  )}
                />
              </Grid>
              <Grid>
                <PlayerActions
                  size="default"
                  displayCount={12}
                  disableAll={selectedPlayers.size === 0}
                  handleAction={(actionType) => {
                    if (isMessageLessAction(actionType)) {
                      handleAction(
                        actionType,
                        selectedPlayers,
                        null,
                        null,
                        null
                      );
                    } else {
                      setConfirmAction({
                        player: "All selected players",
                        actionType: actionType,
                        player_id: null,
                      });
                    }
                  }}
                  onFlag={() => setFlag(true)}
                  onBlacklist={handleBlacklistOpen}
                />
              </Grid>
              <Grid>
                <Padlock
                  handleChange={setShowOnlySelected}
                  checked={showOnlySelected}
                  label="Only show selected players"
                />
              </Grid>
              <Grid>
                <FormControl size="small" style={{ minWidth: "120px" }}>
                  <InputLabel htmlFor="age-native-simple">Sort by</InputLabel>
                  <Select
                    labelId="demo-simple-select-label"
                    id="demo-simple-select"
                    value={sortType}
                    helperText="sort the squads and players"
                    onChange={(e) => {
                      setSortType(e.target.value);
                      localStorage.setItem("game_view_sorting", e.target.value);
                    }}
                  >
                    {Object.keys(sortTypeToFunc).map((k) => (
                      <MenuItem key={k} value={k}>
                        {k}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid>
                <TextField
                  style={{ minWidth: "125px" }}
                  type="number"
                  inputProps={{ min: 2, max: 6000 }}
                  label="Refresh seconds"
                  helperText=""
                  value={refreshFreqSecs}
                  onChange={(e) => setResfreshFreqSecs(e.target.value)}
                />
              </Grid>
            </Grid>
          </Grid>
          {
            [
              { label: "Allies", name: "allies" },
              { label: "Axis", name: "axis" },
              { label: "Unassigned", name: "none" }
            ].map((team) => (
              <Grid
                size={{
                  xs: 12,
                  md: 12,
                  lg: team.name === "none" ? 12 : 6
                }}>
                <Team
                  key={team.name}
                  teamName={team.label}
                  teamData={teamView.get(team.name)}
                  selectedPlayers={selectedPlayers}
                  selectPlayer={selectPlayer}
                  selectMultiplePlayers={selectMultiplePlayers}
                  selectAll={() => selectAllTeam(team.name)}
                  deselectAll={() => deselectAllTeam(team.name)}
                  sortFunc={sortTypeToFunc[sortType]}
                  showOnlySelected={showOnlySelected && selectedPlayers.size !== 0}
                />
              </Grid>
            ))}
        </Fragment>
      ) : (
        <Grid size={12}>
          <LinearProgress />
        </Grid>
      )}
    </Grid>)
  );
};

export default GameView;
