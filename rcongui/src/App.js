import React, { Component } from "react";
import MaterialTable from "material-table";
import "./App.css";
import { makeStyles, withStyles } from "@material-ui/core/styles";
import Paper from "@material-ui/core/Paper";
import Grid from "@material-ui/core/Grid";
import Button from "@material-ui/core/Button";
import Chip from "@material-ui/core/Chip";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemIcon from "@material-ui/core/ListItemIcon";
import ListItemSecondaryAction from "@material-ui/core/ListItemSecondaryAction";
import ListItemText from "@material-ui/core/ListItemText";
import Checkbox from "@material-ui/core/Checkbox";
import ButtonGroup from "@material-ui/core/ButtonGroup";
import TextField from "@material-ui/core/TextField";
import _ from "lodash";
import Menu from "@material-ui/core/Menu";
import MenuItem from "@material-ui/core/MenuItem";
import ArrowDropDownIcon from "@material-ui/icons/ArrowDropDown";
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogContentText from "@material-ui/core/DialogContentText";
import DialogTitle from "@material-ui/core/DialogTitle";
import LinearProgress from "@material-ui/core/LinearProgress";
import Toolbar from "@material-ui/core/Toolbar";
import Typography from '@material-ui/core/Typography';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const useStyles = makeStyles(theme => ({
  root: {
    flexGrow: 1
  },
  paper: {
    padding: theme.spacing(2)
  },
  margin: {
    margin: theme.spacing(2)
  },
  marginBottom: {
    marginBottom: theme.spacing(1)
  },
  textLeft: {
    textAlign: "left",
    paddingLeft: theme.spacing(2)
  }
}));


const AutoRefreshBar = ({ intervalFunction, everyMs, refreshIntevalMs }) => {
  const classes = useStyles();
  const [completed, setCompleted] = React.useState(0);

  React.useEffect(() => {
    function progress() {
      setCompleted(oldCompleted => {
        if (oldCompleted === 100) {
          intervalFunction();
          return 0;
        }

        return Math.min(oldCompleted + (refreshIntevalMs / everyMs) * 100, 100);
      });
    }

    const timer = setInterval(progress, refreshIntevalMs);
    return () => {
      clearInterval(timer);
    };
  }, [everyMs, intervalFunction, refreshIntevalMs]);

  return (
    <React.Fragment>
      <Grid className={classes.textLeft} container justify="flex-start">
       <Grid item xs={12}><h1>Players view</h1></Grid>
       <Grid item xs={12}><ListItemText secondary="Next auto refresh" /></Grid>
       </Grid>  
      <LinearProgress variant="determinate" value={completed} className={classes.marginBottom} />
    </React.Fragment>
  );
};

async function postData(url = "", data = {}) {
  // Default options are marked with *
  const response = await fetch(url, {
    method: "POST", // *GET, POST, PUT, DELETE, etc.
    mode: "cors", // no-cors, *cors, same-origin
    cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
    credentials: "same-origin", // include, *same-origin, omit
    headers: {
      "Content-Type": "application/json",
    },
    redirect: "follow", // manual, *follow, error
    referrerPolicy: "no-referrer", // no-referrer, *client
    body: JSON.stringify(data) // body data type must match "Content-Type" header
  });
  return response; // parses JSON response into native JavaScript objects
}

class ReasonDialog extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      reason: ""
    };

    this.onChange = this.onChange.bind(this);
  }

  onChange(e) {
    e.preventDefault();
    this.setState({ reason: e.target.value });
  }

  render() {
    const { open, handleClose, handleConfirm } = this.props;
    const { reason } = this.state;

    return (
      <Dialog open={open} aria-labelledby="form-dialog-title">
        <DialogTitle id="form-dialog-title">
          Execute {open.actionType} on {open.player}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            id="name"
            label="Reason"
            value={reason}
            onChange={this.onChange}
            fullWidth
          />
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              this.setState({ reason: "" }, handleClose);
            }}
            color="primary"
          >
            Cancel
          </Button>
          <Button
            onClick={() => {
              handleConfirm(open.actionType, open.player, reason);
              this.setState({ reason: "" });
            }}
            color="primary"
          >
            Confirm
          </Button>
        </DialogActions>
      </Dialog>
    );
  }
}

const Filter = ({
  classes,
  filter,
  handleChange,
  total,
  showCount,
  handleMessageChange
}) => {
  /* todo refactor */
  return (
    <Grid item xs={12} spacing={2}>
      <Grid container justify="flex-start" direction="row">
        <Grid item xs={12} md={4} className={classes.textLeft}>
          <TextField
            label="Filter"
            helperText={`Showing: ${showCount} / ${total}`}
            onChange={event => {
              event.preventDefault();
              handleChange(event.target.value);
            }}
          />
        </Grid>
        <Grid item xs={12} md={8} className={classes.textLeft}>
          <TextField
            id="filled-full-width"
            label="Punish/Kick/Ban message"
            helperText={"Leave blank if you want a confirmation popup"}
            fullWidth
            onChange={event => {
              event.preventDefault();
              handleMessageChange(event.target.value);
            }}
          />
        </Grid>
      </Grid>
    </Grid>
  );
};

const PlayerItem = ({ name, steamID64, handleToggle, handleAction }) => (
  <ListItem
    key={name}
    role={undefined}
    dense
  >
    <ListItemText
      id={`checkbox-list-label-${steamID64}`}
      primary={name}
      secondary={steamID64}
    />
    <ListItemSecondaryAction>
      <PlayerActions size="small" handleAction={handleAction} />
    </ListItemSecondaryAction>
  </ListItem>
);

class CompactList extends React.Component {
  shouldComponentUpdate(nextProps, nextState) {
    if (nextProps.playerSteamIDs.length !== this.props.playerSteamIDs.length) {
      return true;
    }
    const diff = _.difference(
      nextProps.playerSteamIDs,
      this.props.playerSteamIDs
    );
    return diff.length > 0;
  }

  render() {
    const {
      playerNames,
      playerSteamIDs,
      classes,
      handleToggle,
      handleAction
    } = this.props;

    return (
      <List className={classes.root}>
        {_.zip(playerNames, playerSteamIDs).map(player => (
          <PlayerItem
            name={player[0]}
            steamID64={player[1]}
            key={player.steam_id_64}
            handleAction={actionType => handleAction(actionType, player[0])}
          />
        ))}
      </List>
    );
  }
}

const SelectedPlayers = ({ players }) => (
  <React.Fragment>
    {players.map(p => (
      <Chip label={p.name} />
    ))}
  </React.Fragment>
);

const PlayerActions = ({ size, handleAction }) => {
  const classes = useStyles();
  const [anchorEl, setAnchorEl] = React.useState(null);
  const handleClick = event => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };

  return (
    <React.Fragment>
      <ButtonGroup size={size} aria-label="small outlined button group">
        <Button onClick={() => handleAction("punish")}>PUNISH</Button>
        <Button onClick={() => handleAction("kick")}>KICK</Button>
        <Button onClick={() => handleAction("temp_ban")}>2H BAN</Button>
        <Button
          aria-controls="simple-menu"
          aria-haspopup="true"
          onClick={handleClick}
        >
          <ArrowDropDownIcon />
        </Button>
        <Menu
          id="simple-menu"
          anchorEl={anchorEl}
          keepMounted
          open={Boolean(anchorEl)}
          onClose={handleClose}
        >
          <MenuItem
            onClick={() => {
              handleAction("switch_player_now");
              handleClose();
            }}
          >
            Switch team now
          </MenuItem>
          <MenuItem
            onClick={() => {
              handleAction("switch_player_on_death");
              handleClose();
            }}
          >
            Switch team on death
          </MenuItem>
          <MenuItem
            onClick={() => {
              handleAction("perma_ban");
              handleClose();
            }}
          >
            Perma Ban
          </MenuItem>
        </Menu>
      </ButtonGroup>
    </React.Fragment>
  );
};

class PlayerView extends Component {
  constructor(props) {
    super();
    this.state = {
      selectedPlayers: [],
      players: [],
      filteredPlayerNames: [],
      filterPlayerSteamIDs: [],
      filter: "",
      filterTimeout: null,
      actionMessage: "",
      doConfirm: false
    };

    this.onPlayerSelected = this.onPlayerSelected.bind(this);
    this.filterPlayers = this.filterPlayers.bind(this);
    this.filterChange = this.filterChange.bind(this);
    this.loadPlayers = this.loadPlayers.bind(this);
  }

  handleAction(actionType, player, message = null) {
    console.log(actionType, player, message);
    if (message === null) {
      message = this.state.actionMessage;
    }
    if (message === "") {
      this.setState({ doConfirm: { player: player, actionType: actionType } });
    } else {
      postData(`${process.env.REACT_APP_API_URL}do_${actionType}`, {
        player: player,
        reason: message
      }).then((response => this.showResponse(response, `${actionType} ${player}`, true))).then(this.loadPlayers);
    }
  }

  onPlayerSelected(players) {
    this.setState({ selectedPlayers: players });
  }

  async showResponse(response, command, showSuccess) {
    if (!response.ok) {
      toast.error(`Game server failed to return for ${command}`)
    } else {
      const res = await response.json()
      if (res.failed === true) {
        toast.warning(`Last command failed: ${command}`)
      } else if (showSuccess === true) {
        toast.success(`Done: ${command}`)
      }
      return res
    }
    return response.json();
  }

  loadPlayers() {
    fetch(`${process.env.REACT_APP_API_URL}get_players`)
      .then(response => this.showResponse(response, "get_players"))
      .then(data =>
        this.setState({ players: data.result === null ? [] : data.result}, this.filterPlayers)
      ).catch(() => toast.error("Unable to connect to API"));
  }

  componentDidMount() {
    this.loadPlayers();
  }

  filterChange(filter) {
    clearTimeout(this.state.filterTimeout); // switch to lodash debounce
    this.setState({
      filter: filter,
      filterTimeout: setTimeout(this.filterPlayers, 200)
    });
  }

  filterPlayers() {
    const { filter, players } = this.state;
    if (!filter) {
      const filteredPlayerNames = players.map(p => p.name);
      const filterPlayerSteamIDs = players.map(p => p.steam_id_64);
      return this.setState({ filterPlayerSteamIDs, filteredPlayerNames });
    }
    const filteredPlayers = _.filter(
      players,
      p => p.name.toLowerCase().indexOf(filter) >= 0
    );

    const filteredPlayerNames = filteredPlayers.map(p => p.name);
    const filterPlayerSteamIDs = filteredPlayers.map(p => p.steam_id_64);
    this.setState({ filteredPlayerNames, filterPlayerSteamIDs });
  }

  render() {
    const { classes } = this.props;
    const {
      selectedPlayers,
      players,
      filteredPlayerNames,
      filterPlayerSteamIDs,
      filter,
      actionMessage,
      doConfirm
    } = this.state;
    console.log(actionMessage);
    return (
      <Grid container spacing={0}>
        <Grid item sm={12} md={6}>
          <AutoRefreshBar
            intervalFunction={this.loadPlayers}
            everyMs={15000}
            refreshIntevalMs={100}
          />
          <Filter
            classes={classes}
            handleChange={this.filterChange}
            total={players.length}
            showCount={filteredPlayerNames.length}
            handleMessageChange={text => this.setState({ actionMessage: text })}
            actionMessage={actionMessage}
          />
          {players  ? (
            <CompactList
              classes={classes}
              playerNames={filteredPlayerNames}
              playerSteamIDs={filterPlayerSteamIDs}
              handleAction={(actionType, player) =>
                this.handleAction(actionType, player)
              }
              handleToggle={() => 1}
            />
          ) : (

            <p>"No players to show"</p>
          )}
        </Grid>
            <Grid item xs={6}>
	    {/*
          <Paper className={classes.paper}>
            <SelectedPlayers players={selectedPlayers} />
            <PlayerActions players={selectedPlayers} />
            </Paper> */}
        </Grid>
        <ToastContainer />
        <ReasonDialog
            open={doConfirm}
            handleClose={() => this.setState({ doConfirm: false })}
            handleConfirm={(action, player, reason) => {
              this.handleAction(action, player, reason);
              this.setState({ doConfirm: false });
            }}
          />
      </Grid>
    );
  }
}

function App() {
  const classes = useStyles();

  return (
    <div className={"App " + classes.root}>
      <PlayerView classes={classes} />
    </div>
  );
}

export default App;
