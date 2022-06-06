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
  LinearProgress
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
import { get, handle_http_errors, postData, showResponse, } from "../../utils/fetchUtils";

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
  </List> : ""
}

const GameView = ({ classes: globalClasses }) => {
  const classes = useStyles();
  const [isLoading, setIsLoading] = React.useState(false)
  const [teamView, setTeamView] = React.useState(null)

  const loadData = () => {
    setIsLoading(true)
    get("get_team_view")
    .then((response) => showResponse(response, "get_team_view_fast"))
    .then((data) => {setIsLoading(false); if (data.result) {setTeamView(fromJS(data.result))}})
    .catch(handle_http_errors);
  }

  React.useEffect(() => {
    loadData();
    const handle = setInterval(loadData, 15000)
    return () => clearInterval(handle)
  }, [])



  return <Grid container spacing={2} className={globalClasses.padding}>
    {teamView ?
      <Fragment>
        { isLoading ? <Grid item xs={12} className={globalClasses.doublePadding}><LinearProgress /></Grid> : ""}
        <Grid item xs={12} md={6}>
          <Team classes={globalClasses} teamName="Axis" teamData={teamView.get("axis")} />
        </Grid>
        <Grid item xs={12} md={6}>
          <Team classes={globalClasses} teamName="Allies" teamData={teamView.get("allies")} />
        </Grid>
        <Grid item xs={12} md={6}>
          <Team classes={globalClasses} teamName="Unassigned" teamData={teamView.get("none")} />
        </Grid>
      </Fragment>

      : <Grid item xs={12} className={globalClasses.doublePadding}><LinearProgress /></Grid>}
  </Grid >
}

export default GameView;