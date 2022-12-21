import React, { Fragment } from "react";
import {
  Grid,
  Link,
  Modal,
  Typography,
  TextField,
  Avatar,
  ListItemSecondaryAction,
  Checkbox,
  LinearProgress,
} from "@material-ui/core";
import Autocomplete from "@material-ui/lab/Autocomplete";
import WarningIcon from "@material-ui/icons/Warning";
import { fromJS, Map, List as IList, OrderedSet } from "immutable";
import { makeStyles } from "@material-ui/core/styles";
import ListSubheader from "@material-ui/core/ListSubheader";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemIcon from "@material-ui/core/ListItemIcon";
import ListItemText from "@material-ui/core/ListItemText";
import Collapse from "@material-ui/core/Collapse";
import { PlayerItem, KDChips, ScoreChips } from "../PlayerView/playerList";
import {
  get,
  handle_http_errors,
  postData,
  showResponse,
} from "../../utils/fetchUtils";
import {
  Duration,
  PlayerActions,
  ReasonDialog,
} from "../PlayerView/playerActions";
import { toast } from "react-toastify";
import { FlagDialog } from "../PlayersHistory";

const useStyles = makeStyles((theme) => ({
  root: {
    backgroundColor: theme.palette.background.paper,
  },
  nested: {
    paddingLeft: theme.spacing(2),
  },
  small: {
    width: theme.spacing(3),
    height: theme.spacing(3),
  },
  large: {
    width: theme.spacing(7),
    height: theme.spacing(7),
  },
  primaryBackground: {
    backgroundColor: theme.palette.primary.dark,
  },
}));

const Squad = ({
  classes: globalClasses,
  squadName,
  squadData,
  doOpen,
  onSelectSquad,
  onSelectPlayer,
  selectedPlayers,
  selectMultiplePlayers,
}) => {
  const classes = useStyles();
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

  const deleteFlag = (flag_id) => {
    return postData(`${process.env.REACT_APP_API_URL}unflag_player`, {
      flag_id: flag_id,
    })
      .then((response) => showResponse(response, "Flag will be removed momentarily", true))
      .catch((error) => toast.error("Unable to connect to API " + error));
  }


  if (squadName === "commander") return "";

  return squadData ? (
    <Fragment>
      <ListItem button onClick={handleClick}>
        <ListItemIcon>
          <Avatar
            variant="rounded"
            className={classes.primaryBackground}
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
              {`${
                squadName.toUpperCase() === "NULL"
                  ? "Unassigned"
                  : squadName.toUpperCase()
              } - ${squadData.get("players", new IList()).size}/${
                sizes[squadData.get("type", "infantry")]
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
                backgroundClass={classes.primaryBackground}
                player={squadData}
              />
              <KDChips classes={classes} player={squadData} />
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
        <List component="div" disablePadding className={classes.nested}>
          {squadData.get("players", new IList()).map((player) => (
            <PlayerItem
              key={player.get("name")}
              classes={globalClasses}
              player={player}
              playerHasExtraInfo={true}
              onDeleteFlag={(flagId) => deleteFlag(flagId)}
              onSelect={() => onSelectPlayer(player.get("name"))}
              isSelected={selectedPlayers?.contains(player.get("name"))}
            />
          ))}
        </List>
      </Collapse>
    </Fragment>
  ) : (
    ""
  );
};

const Team = ({
  classes: globalClasses,
  teamName,
  teamData,
  selectedPlayers,
  selectPlayer,
  selectMultiplePlayers,
  selectAll,
  deselectAll,
}) => {
  const classes = useStyles();
  const [openAll, setOpenAll] = React.useState(false);
  const onOpenAll = () => (openAll ? setOpenAll(false) : setOpenAll(true));

  return teamData ? (
    <List
      dense
      component="nav"
      subheader={
        <ListSubheader component="div" id="nested-list-subheader">
          <Typography variant="h4">
            {teamName} {teamData.get("count", 0)}/50{" "}
            <Link onClick={onOpenAll} component="button">
              {openAll ? "Collapse" : "Expand"} all
            </Link>{" "}
            <Link onClick={selectAll} component="button">
              Select all
            </Link>{" "}
            <Link onClick={deselectAll} component="button">
              deselect all
            </Link>
          </Typography>
        </ListSubheader>
      }
      className={classes.root}
    >
      {teamData.get("commander") ? (
        <PlayerItem
          classes={globalClasses}
          player={teamData.get("commander")}
          playerHasExtraInfo={true}
          onDeleteFlag={() => null}
          avatarBackround={classes.primaryBackground}
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
        .sortBy((v, k) => k)
        .entrySeq()
        .map(([key, value]) => (
          <Squad
            key={key}
            squadName={key}
            squadData={value}
            classes={globalClasses}
            doOpen={openAll}
            onSelectSquad={() => true}
            onSelectPlayer={selectPlayer}
            selectedPlayers={selectedPlayers}
            selectMultiplePlayers={selectMultiplePlayers}
          />
        ))}
    </List>
  ) : (
    ""
  );
};

const SimplePlayerRenderer = ({player, flag}) => <Typography variant="h4">Add {!flag ? '<select a flag>' : flag} to all selected players</Typography>

const GameView = ({ classes: globalClasses }) => {
  const classes = useStyles();
  const [isLoading, setIsLoading] = React.useState(false);
  const [teamView, setTeamView] = React.useState(null);
  const [selectedPlayers, setSelectedPlayers] = React.useState(
    new OrderedSet()
  );
  const [resfreshFreqSecs, setResfreshFreqSecs] = React.useState(5);
  const [intervalHandle, setIntervalHandle] = React.useState(null);
  const [flag, setFlag] = React.useState(false)

  /* confirm action needs to be set to a dict to call the popup: 
        {
          player: null,
          actionType: actionType,
          steam_id_64: null,
        }
  */
  const [confirmAction, setConfirmAction] = React.useState(false);

  const playerNamesToSteamId = React.useMemo(() => {
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
            namesToId[player.get("name")] = player.get("steam_id_64");
          })
        );

      const commander = teamView
        .get(key, new Map())
        .get("commander", new Map());
      if (commander) {
        namesToId[commander.get("name")] = commander.get("steam_id_64");
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
      console.log("Deleting", playerName, selectedPlayers);
      setSelectedPlayers(selectedPlayers.delete(playerName));
    } else if (
      force !== "delete" &&
      (!selectedPlayers.includes(playerName) || force === "add")
    ) {
      console.log("Adding", playerName, selectedPlayers);
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
        console.log("Deletingss", playerName, selectedPlayers);
        newSelectedPlayer = newSelectedPlayer.delete(playerName);
      } else if (
        force !== "delete" &&
        (!selectedPlayers.includes(playerName) || force === "add")
      ) {
        console.log("Addingss", playerName, selectedPlayers);
        newSelectedPlayer = newSelectedPlayer.add(playerName);
      }
    });

    setSelectedPlayers(newSelectedPlayer);
  };

  const loadData = () => {
    setIsLoading(true);
    get("get_team_view_fast")
      .then((response) => showResponse(response, "get_team_view_fast"))
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
    clearInterval(intervalHandle);
    const handle = setInterval(loadData, resfreshFreqSecs * 1000);
    setIntervalHandle(handle);
    return () => clearInterval(handle);
  }, [resfreshFreqSecs]);

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
        player: null,
        actionType: actionType,
        steam_id_64: null,
      });
    } else {
      playerNames.forEach((playerName) => {
        if (allPlayerNames.indexOf(playerName) === -1) {
          toast.error(`Player ${playerName} is not on the server anymore`)
          selectPlayer(playerName, 'delete')
          return
        }
        const steam_id_64 = playerNamesToSteamId.get(playerName, null);
        const data = {
          player: playerName,
          steam_id_64: steam_id_64,
          reason: message,
          comment: comment,
          duration_hours: duration_hours,
          message: message,
        };
        if (actionType === "temp_ban") {
          data["forward"] = "yes";
        }
        console.log(`Posting do_${actionType}`, data);
        postData(`${process.env.REACT_APP_API_URL}do_${actionType}`, data)
          .then((response) =>
            showResponse(response, `${actionType} ${playerName}`, true)
          )
          .catch(handle_http_errors);

        if (comment) {
          postData(`${process.env.REACT_APP_API_URL}post_player_comment`, {
            steam_id_64: steam_id_64,
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
        steam_id_64: playerNamesToSteamId.get(name),
        flag: flag,
        comment: comment,
      })
        .then((response) => showResponse(response, "flag_player", true))
        .then(() => setFlag(false))
        .catch(handle_http_errors)
    );
  };

  return (
    <Grid container spacing={2} className={globalClasses.padding}>
      {teamView ? (
        <Fragment>
          <Grid item xs={12} className={globalClasses.doublePadding}>
            <LinearProgress
              style={{ visibility: isLoading ? "visible" : "hidden" }}
            />
          </Grid>

          <Grid item xs={12}>
          <FlagDialog
            open={flag}
            handleClose={() => setFlag(false)}
            handleConfirm={addFlagToPlayers}
            SummaryRenderer={SimplePlayerRenderer}
          />
            <Grid container alignItems="center" spacing={2}>
              <ReasonDialog
                open={confirmAction}
                handleClose={() => setConfirmAction(false)}
                handleConfirm={(
                  action,
                  player,
                  reason,
                  comment,
                  duration_hours = 2,
                  steam_id_64 = null
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

              <Grid item md={12} lg={6}>
                <Autocomplete
                  className={classes.marginBottom}
                  multiple
                  clearOnEscape
                  id="tags-outlined"
                  options={allPlayerNames}
                  value={selectedPlayers.toJS()}
                  filterSelectedOptions
                  onChange={(e, val) => {
                    setSelectedPlayers(new OrderedSet(val));
                  }}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      variant="outlined"
                      label="Selected players to apply action to"
                      fullWidth
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={12} lg={6}>
                <PlayerActions
                  size="large"
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
                        steam_id_64: null,
                      });
                    }
                  }}
                  onFlag={() => setFlag(true)}
                />
              </Grid>
            </Grid>
          </Grid>
          <Grid item xs={12} md={12} lg={6}>
            <Team
              classes={globalClasses}
              teamName="Axis"
              teamData={teamView.get("axis")}
              selectedPlayers={selectedPlayers}
              selectPlayer={selectPlayer}
              selectMultiplePlayers={selectMultiplePlayers}
              selectAll={() => selectAllTeam("axis")}
              deselectAll={() => deselectAllTeam("axis")}
            />
          </Grid>
          <Grid item xs={12} md={12} lg={6}>
            <Team
              classes={globalClasses}
              teamName="Allies"
              teamData={teamView.get("allies")}
              selectedPlayers={selectedPlayers}
              selectPlayer={selectPlayer}
              selectMultiplePlayers={selectMultiplePlayers}
              selectAll={() => selectAllTeam("allies")}
              deselectAll={() => deselectAllTeam("allies")}
            />
          </Grid>
          <Grid item xs={12} md={12}>
            <Team
              classes={globalClasses}
              teamName="Unassigned"
              teamData={teamView.get("none")}
              selectedPlayers={selectedPlayers}
              selectPlayer={selectPlayer}
              selectMultiplePlayers={selectMultiplePlayers}
              selectAll={() => selectAllTeam("none")}
              deselectAll={() => deselectAllTeam("none")}
            />
          </Grid>
        </Fragment>
      ) : (
        <Grid item xs={12} className={globalClasses.doublePadding}>
          <LinearProgress />
        </Grid>
      )}
    </Grid>
  );
};

export default GameView;
