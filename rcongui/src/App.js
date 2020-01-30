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

const useStyles = makeStyles(theme => ({
  root: {
    flexGrow: 1
  },
  paper: {
    padding: theme.spacing(2)
  },
  margin: {
    margin: theme.spacing(1)
  }
}));

const Filter = ({ filter, handleChange }) => {
  return (
    <div style={{ width: 300 }}>
      <TextField
        label="Filter"
        onChange={event => {
          event.preventDefault();
          handleChange(event.target.value);
        }}
      />
    </div>
  );
};

class PlayerList extends Component {
  constructor(props) {
    super();
    this.state = {
      players: []
    };
  }

  componentDidMount() {
    fetch(`${process.env.REACT_APP_API_URL}get_players`)
      .then(response => response.json())
      .then(data => this.setState({ players: data.result }));
  }

  render() {
    const { onPlayerSelected } = this.props;

    return (
      <MaterialTable
        columns={[
          { title: "Player", field: "name" },
          { title: "SteamID", field: "steam_id_64" }
        ]}
        data={this.state.players}
        title="Player List"
        options={{
          selection: true,
          pageSize: 100,
          pageSizeOptions: [5, 10, 25, 50, 100]
        }}
        onSelectionChange={rows => onPlayerSelected(rows)}
      />
    );
  }
}

const CompactList = ({ players, classes, handleToggle }) => (
  <List className={classes.root}>
    {players.map(value => {
      const labelId = `checkbox-list-label-${value.name}`;

      return (
        <ListItem
          key={value.name}
          role={undefined}
          dense
          button
          onClick={value => handleToggle(value)}
        >
          <ListItemIcon>
            <Checkbox
              edge="start"
              checked={false}
              tabIndex={-1}
              disableRipple
              inputProps={{ "aria-labelledby": labelId }}
            />
          </ListItemIcon>
          <ListItemText
            id={labelId}
            primary={value.name}
            secondary={value.steam_id_64}
          />
          <ListItemSecondaryAction>
            <PlayerActions size="small" />
          </ListItemSecondaryAction>
        </ListItem>
      );
    })}
  </List>
);

const SelectedPlayers = ({ players }) => (
  <React.Fragment>
    {players.map(p => (
      <Chip label={p.name} />
    ))}
  </React.Fragment>
);

const PlayerActions = ({ size }) => {
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
        <Button>PUNISH</Button>
        <Button>KICK</Button>
        <Button>2H BAN</Button>
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
          <MenuItem onClick={handleClose}>Switch team now</MenuItem>
          <MenuItem onClick={handleClose}>Switch team on death</MenuItem>
          <MenuItem onClick={handleClose}>Perma Ban</MenuItem>
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
      filteredPlayers: [],
      filter: "",
      filterTimeout: null
    };

    this.onPlayerSelected = this.onPlayerSelected.bind(this);
    this.filterPlayers = this.filterPlayers.bind(this);
    this.filterChange = this.filterChange.bind(this);
  }

  onPlayerSelected(players) {
    this.setState({ selectedPlayers: players });
  }

  componentDidMount() {
    fetch(`${process.env.REACT_APP_API_URL}get_players`)
      .then(response => response.json())
      .then(data =>
        this.setState({ players: data.result, filteredPlayers: data.result })
      );
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
    console.log(players.length, this.state.filteredPlayers.length);
    if (!filter) {
      return this.setState({ filteredPlayers: players });
    }
    const filteredPlayers = _.filter(
      players,
      p => p.name.toLowerCase().indexOf(filter) >= 0
    );

    this.setState({ filteredPlayers });
  }

  render() {
    const { classes } = this.props;
    const { selectedPlayers, players, filteredPlayers, filter } = this.state;

    return (
      <Grid container spacing={3}>
        <Grid item xs={6}>
          {/* <PlayerList onPlayerSelected={this.onPlayerSelected} /> */}
          <Filter handleChange={this.filterChange} />

          <CompactList classes={classes} players={filteredPlayers} />
        </Grid>
        <Grid item xs={6}>
          <Paper className={classes.paper}>
            <SelectedPlayers players={selectedPlayers} />
            <PlayerActions players={selectedPlayers} />
          </Paper>
        </Grid>
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
