import React, { Fragment } from "react";
import {
  Dialog,
  DialogTitle,
  Grid,
  Link,
  Modal,
  Typography,
  DialogContent,
  DialogActions,
  DialogContentText,
  Button,
  TextareaAutosize,
  Avatar,
  ListItemSecondaryAction,
  Checkbox,
  LinearProgress,
  Slider,
  Box,
  Input,
  FormGroup,
  FormControlLabel,
  InputLabel,
  Select,
  FormLabel,
  RadioGroup,
  Radio,
  TextField,
  InputAdornment,
} from "@material-ui/core";
import WarningIcon from '@material-ui/icons/Warning';
import { fromJS, Map, List as IList } from "immutable";
import { makeStyles } from '@material-ui/core/styles';
import ListSubheader from '@material-ui/core/ListSubheader';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import Collapse from '@material-ui/core/Collapse';
import InboxIcon from '@material-ui/icons/MoveToInbox';
import DraftsIcon from '@material-ui/icons/Drafts';
import SendIcon from '@material-ui/icons/Send';
import ExpandLess from '@material-ui/icons/ExpandLess';
import ExpandMore from '@material-ui/icons/ExpandMore';
import StarBorder from '@material-ui/icons/StarBorder';
import { PlayerItem, KDChips, ScoreChips } from '../PlayerView/playerList'
import reactRouterDom from "react-router-dom";
import { AlertDialog, InputSlider, Padlock } from "../commonComponent";
import FormControl from "@material-ui/core/FormControl";

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
    backgroundColor: theme.palette.primary.dark
  },
}));


const Squad = ({ classes: globalClasses, squadName, squadData, doOpen }) => {
  const classes = useStyles();
  const [open, setOpen] = React.useState(false);
  const handleClick = () => {
    setOpen(!open);
  };
  const sizes = {
    armor: 3,
    infantry: 6,
    recon: 2
  }

  if (squadName === "commander") return "";

  return squadData ? <Fragment>
    <ListItem button onClick={handleClick}      >
      <ListItemIcon>
        <Avatar variant="rounded" className={classes.primaryBackground} alt={squadData.get("type", "na")} src={`icons/roles/${squadData.get("type")}.png`}>
          {squadName[0].toUpperCase()}
        </Avatar>
      </ListItemIcon>
      <ListItemText primary={

        <Typography variant="h6">
          {`${squadName.toUpperCase()} - ${squadData.get("players", new IList()).size}/${sizes[squadData.get("type", "infantry")]}`} {squadData.get("has_leader", false) ? "" : <WarningIcon style={{ verticalAlign: "middle" }} fontSize="small" color="error" />}
        </Typography>

      }
        secondary={<Grid container spacing={1}><ScoreChips backgroundClass={classes.primaryBackground} player={squadData} /><KDChips classes={classes} player={squadData} /></Grid>} />

      {/*<ListItemSecondaryAction>
        <Checkbox
          edge="end"
        />
      </ListItemSecondaryAction> */}

    </ListItem>
    <Collapse in={open || doOpen} timeout="auto" unmountOnExit>
      <List component="div" disablePadding className={classes.nested}>
        {squadData.get("players", new IList()).map(
          (player) => (
            <PlayerItem
              key={player.get("name")}
              classes={globalClasses}
              player={player}
              playerHasExtraInfo={true}
              onDeleteFlag={() => (null)}
            />
          )
        )}
      </List>
    </Collapse>
  </Fragment> : ""
}

const Team = ({ classes: globalClasses, teamName, teamData }) => {
  const classes = useStyles();
  const [openAll, setOpenAll] = React.useState(false)
  const onOpenAll = () => openAll ? setOpenAll(false) : setOpenAll(true)

  return teamData ? <List
    dense
    component="nav"
    subheader={
      <ListSubheader component="div" id="nested-list-subheader">
        <Typography variant="h4">{teamName} {teamData.get("count", 0)}/50 <Link onClick={onOpenAll} component="button">{openAll ? "Collapse" : "Expand"} all</Link></Typography>

      </ListSubheader>
    }
    className={classes.root}
  >
    {teamData.get("commander") ?
      <PlayerItem
        classes={globalClasses}
        player={teamData.get("commander")}
        playerHasExtraInfo={true}
        onDeleteFlag={() => (null)}
        avatarBackround={classes.primaryBackground}
      /> : ""}
    {teamData.get("squads", new Map()).toOrderedMap().sortBy((v, k) => k).entrySeq().map(
      ([key, value]) => (
        <Squad key={key} squadName={key} squadData={value} classes={globalClasses} doOpen={openAll} />
      )
    )}
const ShuffleForm = () => {
  const [shuffleMethod, setShuffleMethod] = React.useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Shuffle teams");
    postData(`${process.env.REACT_APP_API_URL}do_shuffle_teams`, {
      shuffle_method: shuffleMethod,
    })
      .then((response) => showResponse(response, "do_shuffle_teams"))
      .catch(handle_http_errors);
  };

  return (
    <form onSubmit={handleSubmit}>
      <Grid container>
        <Grid item xs={12} md={6} lg={3}>
          <FormControl>
            <FormLabel>Shuffle Method</FormLabel>
            <RadioGroup
              value={shuffleMethod}
              defaultChecked="split_shuffle"
              onChange={(event) => setShuffleMethod(event.target.value)}
            >
              <FormControlLabel
                value="split_shuffle"
                control={<Radio />}
                label="Split Shuffle"
              />
              <FormControlLabel
                value="random_shuffle"
                control={<Radio />}
                label="Random Shuffle"
              />
              <FormControlLabel
                value="player_level"
                control={<Radio />}
                label="By Player Level"
              />
            </RadioGroup>
          </FormControl>
        </Grid>
        <Grid item xs={12}>
          <Button onClick={handleSubmit} variant="contained">
            Shuffle Teams
          </Button>
        </Grid>
      </Grid>
    </form>
  );
};

const BalanceForm = () => {
  const immuneRolesLabels = [
    { label: "Commander", role: "armycommander" },
    { label: "Tank Commander", role: "tankcommander" },
    { label: "Crewman", role: "crewmman" },
    { label: "Spotter", role: "spotter" },
    { label: "Sniper", role: "sniper" },
    { label: "Squad Lead", role: "officer" },
    { label: "Rifleman", role: "rifleman" },
    { label: "Assault", role: "assault" },
    { label: "Automatic Rifleman", role: "automaticrifleman" },
    { label: "Medic", role: "medic" },
    { label: "Support", role: "support" },
    { label: "Machine Gunner", role: "heavymachinegunner" },
    { label: "Anti-Tank", role: "antitank" },
    { label: "Engineer", role: "engineer" },
  ];

  const [rebalanceMethod, setRebalanceMethod] = React.useState("");
  const [immuneLevel, setImmuneLevel] = React.useState(0);
  const [immuneRoles, setImmuneRoles] = React.useState([]);
  const [immuneSeconds, setImmuneSeconds] = React.useState(0);
  const [includeTeamless, setIncludeTeamless] = React.useState(true);
  const [swapOnDeath, setSwapOnDeath] = React.useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Rebalance Teams");
    postData(`${process.env.REACT_APP_API_URL}do_balance_teams`, {
      rebalance_method: rebalanceMethod,
      immune_level: immuneLevel,
      immune_roles: immuneRoles,
      immune_seconds: immuneSeconds,
      include_teamless: includeTeamless,
      swap_on_death: swapOnDeath,
    })
      .then((response) => showResponse(response, "do_balance_teams"))
      .catch(handle_http_errors);
  };

  const handleChangeMultiple = (event) => {
    const { options } = event.target;
    const selectedRoles = [];
    for (let i = 0; i < options.length; i++) {
      if (options[i].selected) {
        selectedRoles.push(options[i].value);
      }
    }
    setImmuneRoles(selectedRoles);
  };

  const handleNumberTextFieldChange = (event, fn) => {
    const value = event.target.value;
    console.log(
      `value: ${Number(value)} seconds: ${immuneSeconds} level: ${immuneLevel}`
    );
    Number(value) !== NaN && Number(value) >= 0 ? fn(value) : fn(0);
  };

  return (
    <form onSubmit={handleSubmit}>
      <Grid container>
        <Grid item xs={12} md={6} lg={3}>
          <FormControl>
            <FormLabel>Rebalance Method</FormLabel>
            <RadioGroup
              value={rebalanceMethod}
              defaultChecked="arrival_most_recent"
              defaultValue="arrival_most_recent"
              onChange={(event) => setRebalanceMethod(event.target.value)}
            >
              <FormControlLabel
                value="arrival_most_recent"
                control={<Radio />}
                label="Most Recently Joined"
              />
              <FormControlLabel
                value="arrival_least_recent"
                control={<Radio />}
                label="Least Recently Joined"
              />
              <FormControlLabel
                value="random"
                control={<Radio />}
                label="Random"
              />
            </RadioGroup>
          </FormControl>
        </Grid>
        <Grid
          container
          direction="column"
          rowSpacing={{ xs: 6 }}
          item
          xs={12}
          md={6}
          lg={3}
        >
          <Grid item>
            <TextField
              value={immuneLevel}
              label="Min Player Level To Swap"
              type="number"
              onChange={(event) =>
                handleNumberTextFieldChange(event, setImmuneLevel)
              }
            />
          </Grid>
          <Grid item>
            <TextField
              value={immuneSeconds}
              label="Min Seconds Between Player Swaps"
              type="number"
              onChange={(event) =>
                handleNumberTextFieldChange(event, setImmuneSeconds)
}
            />
          </Grid>
        </Grid>
        <Grid item xs={12} lg={3}>
          <Grid item xs={12}>
            <Padlock
              checked={swapOnDeath}
              handleChange={() => setSwapOnDeath(!swapOnDeath)}
              label="Swap On Death"
            />
          </Grid>
          <Grid item xs={12}>
            <Padlock
              checked={includeTeamless}
              handleChange={() => setIncludeTeamless(!includeTeamless)}
              label="Include Teamless Players"
            />
          </Grid>
        </Grid>
        <Grid item xs={12} lg={3}>
          <FormControl>
            <InputLabel shrink>Immune Roles</InputLabel>
            <Select
              multiple
              native
              value={immuneRoles}
              onChange={handleChangeMultiple}
              inputProps={{
                id: "select-multiple-native",
                size: immuneRolesLabels.length,
              }}
            >
              {immuneRolesLabels.map((role) => (
                <option key={role.role} value={role.role}>
                  {role.label}
                </option>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12}>
          <Button onClick={handleSubmit} variant="contained">
            Rebalance Teams
          </Button>
        </Grid>
      </Grid>
    </form>
  );
};

const GameView = ({ classes: globalClasses }) => {
  const classes = useStyles();
  const [isLoading, setIsLoading] = React.useState(false)
  const [teamView, setTeamView] = React.useState(null)

  const loadData = () => {
    setIsLoading(true)
    get("get_team_view_fast")
    .then((response) => showResponse(response, "get_team_view_fast"))
    .then((data) => {setIsLoading(false); if (data.result) {setTeamView(fromJS(data.result))}})
    .catch(handle_http_errors);
  }

  React.useEffect(() => {
    loadData();
    const handle = setInterval(loadData, 15000)
    return () => clearInterval(handle)
  }, [])


  const onConfirm = () => console.log("Confirmed");

  return (
    <Grid container spacing={2} className={globalClasses.padding}>
      {teamView ? (
      <Fragment>
          {isLoading ? (
            <Grid item xs={12} className={globalClasses.doublePadding}>
              <LinearProgress />
            </Grid>
          ) : (
            ""
          )}
          <Grid container>
            <Grid item xs={12} md={6}>
              <BalanceForm />
            </Grid>
            <Grid item xs={12} md={6}>
              <ShuffleForm />
            </Grid>
          </Grid>
        <Grid item xs={12} md={6}>
            <Team
              classes={globalClasses}
              teamName="Axis"
              teamData={teamView.get("axis")}
            />
        </Grid>
        <Grid item xs={12} md={6}>
            <Team
              classes={globalClasses}
              teamName="Allies"
              teamData={teamView.get("allies")}
            />
        </Grid>
        <Grid item xs={12} md={6}>
            <Team
              classes={globalClasses}
              teamName="Unassigned"
              teamData={teamView.get("none")}
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