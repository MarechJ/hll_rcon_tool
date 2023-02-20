import React, { Fragment, useState } from "react";
import {
  Grid,
  Link,
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
  RadioGroup,
  FormControlLabel,
  Radio,
  FormLabel,
  Button,
  FormGroup,
  Switch,
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
import { PlayerActions, ReasonDialog } from "../PlayerView/playerActions";
import { toast } from "react-toastify";
import { FlagDialog } from "../PlayersHistory";
import Padlock from "../SettingsView/padlock";
import CollapseCard from "../collapseCard";

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
  showOnlySelected,
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
          {squadData.get("players", new IList()).map((player) => {
            if (
              showOnlySelected &&
              !selectedPlayers.includes(player.get("name"))
            )
              return "";

            return (
              <PlayerItem
                key={player.get("name")}
                classes={globalClasses}
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
  classes: globalClasses,
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
  const classes = useStyles();
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
            justify="space-between"
            spacing={2}
          >
            <Grid item xs={9}>
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
            <Grid item={3}></Grid>
          </Grid>
        </ListSubheader>
      }
      className={classes.root}
    >
      {teamData.get("commander") &&
      (!showOnlySelected ||
        (showOnlySelected &&
          selectedPlayers.contains(teamData.get("commander")?.get("name")))) ? (
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
        .sortBy(sortFunc)
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

const GameView = ({ classes: globalClasses }) => {
  const classes = useStyles();
  const [isLoading, setIsLoading] = React.useState(false);
  const [teamView, setTeamView] = React.useState(null);
  const [selectedPlayers, setSelectedPlayers] = React.useState(
    new OrderedSet()
  );
  const [resfreshFreqSecs, setResfreshFreqSecs] = React.useState(5);
  const [intervalHandle, setIntervalHandle] = React.useState(null);
  const [flag, setFlag] = React.useState(false);
  const [sortType, setSortType] = React.useState(
    localStorage.getItem("game_view_sorting")
      ? localStorage.getItem("game_view_sorting")
      : "name_asc"
  );
  /* confirm action needs to be set to a dict to call the popup:
        {
          player: null,
          actionType: actionType,
          steam_id_64: null,
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

  const myInterval = React.useMemo(
    () => (func, ms) => {
      const handle = setTimeout(async () => {
        try {
          await func();
        } catch (e) {
          console.warn("Error in periodic refresh", e);
        }
        myInterval(func, ms);
      }, ms);
      setIntervalHandle(handle);
    },
    []
  );

  React.useEffect(() => {
    loadData();
  }, []);

  React.useEffect(() => {
    clearTimeout(intervalHandle);
    myInterval(loadData, resfreshFreqSecs * 1000);
    return () => clearInterval(intervalHandle);
  }, [resfreshFreqSecs, myInterval]);

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
          toast.error(`Player ${playerName} is not on the server anymore`);
          selectPlayer(playerName, "delete");
          return;
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
          <FlagDialog
            open={flag}
            handleClose={() => setFlag(false)}
            handleConfirm={addFlagToPlayers}
            SummaryRenderer={SimplePlayerRenderer}
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
          <Grid item xs={12}>
            <Grid
              container
              alignItems="center"
              justify="space-between"
              spacing={2}
            >
              <Grid item xs={12}>
                <Autocomplete
                  className={classes.marginBottom}
                  multiple
                  clearOnEscape
                  id="tags-outlined"
                  options={allPlayerNames}
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
              <Grid item>
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
                        steam_id_64: null,
                      });
                    }
                  }}
                  onFlag={() => setFlag(true)}
                />
              </Grid>
              <Grid item>
                <Padlock
                  handleChange={setShowOnlySelected}
                  checked={showOnlySelected}
                  label="Only show selected players"
                />
              </Grid>
              <Grid item>
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
              <Grid item>
                <TextField
                  style={{ minWidth: "125px" }}
                  type="number"
                  inputProps={{ min: 2, max: 6000 }}
                  label="Refresh seconds"
                  helperText=""
                  value={resfreshFreqSecs}
                  onChange={(e) => setResfreshFreqSecs(e.target.value)}
                />
              </Grid>
            </Grid>
          </Grid>
          <Grid item xs={12}>
            <CollapseCard classes={classes} title="Shuffle/Balance Teams">
              <Grid container>
                <Grid item xs={12} lg={6}>
                  <ShuffleControls />
                </Grid>
                <Grid item xs={12} lg={6}>
                  <BalanceControls />
                </Grid>
              </Grid>
            </CollapseCard>
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
              sortFunc={sortTypeToFunc[sortType]}
              showOnlySelected={showOnlySelected && selectedPlayers.size !== 0}
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
              sortFunc={sortTypeToFunc[sortType]}
              showOnlySelected={showOnlySelected && selectedPlayers.size !== 0}
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
              sortFunc={sortTypeToFunc[sortType]}
              showOnlySelected={showOnlySelected && selectedPlayers.size !== 0}
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

const ShuffleControls = () => {
  /* TODO: should make an endpoint to provide these dynamically */
  const METHODS = [
    { method: "random_shuffle", label: "Random Shuffle" },
    { method: "player_level", label: "By Player Level" },
    { method: "split_shuffle", label: "Split Shuffle" },
  ];

  const [shuffleMethod, setShuffleMethod] = useState(METHODS[0].method);

  const handleChange = (e) => setShuffleMethod(e.target.value);
  const handleSubmit = (e) => {
    e.preventDefault();
    return postData(`${process.env.REACT_APP_API_URL}do_shuffle_teams`, {
      shuffle_method: shuffleMethod,
    })
      .then((response) =>
        showResponse(response, `Team Shuffle by ${shuffleMethod}`, true)
      )
      .catch(handle_http_errors);
  };

  return (
    <Grid item xs={12} lg={6}>
      <form>
        <FormControl>
          <FormLabel>Shuffle Controls</FormLabel>
          <RadioGroup
            name="shuffle_method"
            value={shuffleMethod}
            onChange={handleChange}
          >
            {METHODS.map((m) => {
              return (
                <FormControlLabel
                  value={m.method}
                  control={<Radio />}
                  label={m.label}
                />
              );
            })}
          </RadioGroup>
        </FormControl>
        <Button type="submit" variant="contained" onClick={handleSubmit}>
          Shuffle Teams
        </Button>
      </form>
    </Grid>
  );
};

const BalanceControls = () => {
  /* TODO: should make an endpoint to provide these dynamically */
  const METHODS = [
    { method: "arrival_most_recent", label: "Most Recently Joined" },
    { method: "arrival_least_recent", label: "Least Recently Joined" },
    { method: "random", label: "Random Selection" },
  ];
  const roleGroups = [
    {
      id: 0,
      label: "Commander",
      roles: new Set([0]),
    },
    {
      id: 1,
      label: "Armor",
      roles: new Set([1, 2]),
    },
    {
      id: 2,
      label: "Recon",
      roles: new Set([3, 4]),
    },
    {
      id: 3,
      label: "Infantry",
      roles: new Set([5, 6, 7, 8, 9, 10, 11, 12, 13]),
    },
  ];

  const [roles, setRoles] = useState([
    {
      id: 0,
      checked: false,
      value: "armycommander",
      label: "Commander",
    },
    {
      id: 1,
      checked: false,
      value: "tankcommander",
      label: "Tank Commander",
    },
    {
      id: 2,
      checked: false,
      value: "crewman",
      label: "Crewman",
    },
    {
      id: 3,
      checked: false,
      value: "spotter",
      label: "Spotter",
    },
    {
      id: 4,
      checked: false,
      value: "sniper",
      label: "Sniper",
    },
    {
      id: 5,
      checked: false,
      value: "officer",
      label: "Officer",
    },
    {
      id: 6,
      checked: false,
      value: "rifleman",
      label: "Rifleman",
    },
    {
      id: 7,
      checked: false,
      value: "assault",
      label: "Assault",
    },
    {
      id: 8,
      checked: false,
      value: "automaticrifleman",
      label: "Automatic Rifleman",
    },
    {
      id: 9,
      checked: false,
      value: "medic",
      label: "Medic",
    },
    {
      id: 10,
      checked: false,
      value: "support",
      label: "Support",
    },
    {
      id: 11,
      checked: false,
      value: "heavymachinegunner",
      label: "Machine Gunner",
    },
    {
      id: 12,
      checked: false,
      value: "antitank",
      label: "Anti-Tank",
    },
    {
      id: 13,
      checked: false,
      value: "engineer",
      label: "Engineer",
    },
  ]);

  const [balanceMethod, setBalanceMethod] = useState(METHODS[0].method);
  const [immuneLevel, setImmuneLevel] = useState(0);
  const [immuneSeconds, setImmuneSeconds] = useState(0);
  const [includeTeamless, setIncludeTeamless] = useState(false);
  const [swapOnDeath, setSwapOnDeath] = useState(false);

  const handleBalanceChange = (e) => setBalanceMethod(e.target.value);
  // TODO: add error handling for out of bounds conditions
  const handleImmuneLevelChange = (value) => setImmuneLevel(value);
  const handleImmuneSecondsChange = (value) => setImmuneSeconds(value);

  const determineCheckboxState = (groupId) => {
    /*
     * Return whether a parent checkbox should be checked or indeterminate
     * based on the state of its children
     */
    const group = roleGroups.find((g) => g.id === groupId);
    const selectedRoles = roles.filter((r) => group.roles.has(r.id));

    let state = {};
    if (selectedRoles.every((r) => r.checked === true)) {
      // all checked = checked
      state = { checked: true, indeterminate: false };
    } else if (selectedRoles.some((r) => r.checked === true)) {
      // some checked = indeterminate
      state = { checked: false, indeterminate: true };
    } else {
      // all unchecked = unchecked
      state = { checked: false, indeterminate: false };
    }

    return state;
  };

  const handleRoleGroupsChange = (groupId, checkboxState) => {
    /*
     * Check or uncheck each child checkbox when the parent is clicked
     */
    let newState = false;

    if (!checkboxState.checked) {
      newState = true;
    }

    const group = roleGroups.find((g) => g.id === groupId);
    const selectedRoleIds = roles
      .filter((r) => group.roles.has(r.id))
      .map((r) => r.id);

    setRoles(
      roles.map((r) => {
        if (selectedRoleIds.includes(r.id)) {
          return {
            ...r,
            checked: newState,
          };
        } else {
          return r;
        }
      })
    );
  };

  const handleRolesChange = (id) => {
    /*
     * Toggle the state of a checkbox when clicked
     */
    setRoles(
      roles.map((r) => {
        if (r.id === id) {
          return {
            ...r,
            checked: !r.checked,
          };
        } else {
          return r;
        }
      })
    );
  };

  const selectedRoleNames = () =>
    roles.filter((r) => r.checked).map((r) => r.value);

  const handleSubmit = (e) => {
    e.preventDefault();
    return postData(`${process.env.REACT_APP_API_URL}do_even_teams`, {
      rebalance_method: balanceMethod,
      immune_level: immuneLevel,
      immune_roles: selectedRoleNames(),
      immune_seconds: immuneSeconds,
      include_teamless: includeTeamless,
      swap_on_death: swapOnDeath,
    })
      .then((response) =>
        showResponse(response, `Team Balance by ${balanceMethod}`, true)
      )
      .catch(handle_http_errors);
  };

  return (
    <form>
      <Grid item xs={12}>
        <FormControl>
          <FormLabel>Balance Method</FormLabel>
          <RadioGroup
            name="shuffle_method"
            value={balanceMethod}
            onChange={handleBalanceChange}
          >
            {METHODS.map((m) => {
              return (
                <FormControlLabel
                  value={m.method}
                  control={<Radio />}
                  label={m.label}
                />
              );
            })}
          </RadioGroup>
        </FormControl>
      </Grid>
      <Grid item xs={12}>
        <FormGroup>
          <FormControl>
            <TextField
              id="outlined-number"
              helperText="Seconds until player is swappable again"
              label="Immune Level"
              type="number"
              value={immuneLevel}
              onChange={(e) => handleImmuneLevelChange(e.target.value)}
              InputLabelProps={{
                shrink: true,
              }}
              variant="outlined"
            />
          </FormControl>
          <FormControl>
            <TextField
              id="outlined-number"
              helperText="Players below this level will not be swapped"
              label="Immune Level"
              type="number"
              value={immuneSeconds}
              onChange={(e) => handleImmuneSecondsChange(e.target.value)}
              InputLabelProps={{
                shrink: true,
              }}
              variant="outlined"
            />
          </FormControl>
        </FormGroup>
      </Grid>
      <Grid item xs={12}>
        <FormGroup>
          <FormControlLabel
            control={
              <Switch
                checked={includeTeamless}
                onChange={(e) => setIncludeTeamless(e.target.checked)}
                name="includeTeamless"
                color="primary"
              />
            }
            label="Include Teamless Players"
          />
          <FormControlLabel
            control={
              <Switch
                checked={swapOnDeath}
                onChange={(e) => setSwapOnDeath(e.target.checked)}
                name="swapOnDeath"
                color="primary"
              />
            }
            label="Swap On Death"
          />
        </FormGroup>
      </Grid>
      <Grid item xs={12}>
        <FormGroup>
          {roleGroups.map((g) => {
            const checkboxState = determineCheckboxState(g.id);
            return (
              <>
                <FormGroup>
                  <FormControlLabel
                    label={g.label}
                    control={
                      <Checkbox
                        checked={checkboxState.checked}
                        indeterminate={checkboxState.indeterminate}
                        onChange={() =>
                          handleRoleGroupsChange(g.id, checkboxState)
                        }
                      />
                    }
                  />
                </FormGroup>
                <FormGroup>
                  {roles
                    .filter((r) => g.roles.has(r.id))
                    .map((r) => {
                      return (
                        <FormControlLabel
                          label={r.label}
                          control={
                            <Checkbox
                              checked={r.checked}
                              onChange={() => handleRolesChange(r.id)}
                            />
                          }
                        />
                      );
                    })}
                </FormGroup>
              </>
            );
          })}
        </FormGroup>
      </Grid>
      <Grid item xs={12}>
        <Button type="submit" variant="contained" onClick={handleSubmit}>
          Balance Teams
        </Button>
      </Grid>
    </form>
  );
};

export default GameView;
