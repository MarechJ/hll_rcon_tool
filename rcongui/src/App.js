import React, {Component} from 'react';
import MaterialTable from "material-table";
import './App.css';
import { throwStatement } from '@babel/types';
import { makeStyles, withStyles } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import { yellow } from '@material-ui/core/colors';
import Chip from '@material-ui/core/Chip';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemSecondaryAction from '@material-ui/core/ListItemSecondaryAction';
import ListItemText from '@material-ui/core/ListItemText';
import Checkbox from '@material-ui/core/Checkbox';
import IconButton from '@material-ui/core/IconButton';
import CommentIcon from '@material-ui/icons/Comment';
import ButtonGroup from '@material-ui/core/ButtonGroup';
import TextField from '@material-ui/core/TextField';
import Autocomplete from '@material-ui/lab/Autocomplete';
import _ from 'lodash'

const useStyles = makeStyles(theme => ({
  root: {
    flexGrow: 1,
  },
  paper: {
    padding: theme.spacing(2),
  },
  margin: {
    margin: theme.spacing(1),
  },
}));


const Filter = ({players, handleChange}) => {
  return (
    <div style={{ width: 300 }}>
      <TextField label="Filter" onChange={(event) => handleChange(event.target.value)} />
    </div>
  );
}

class PlayerList extends Component {
  constructor(props) {
    super()
    this.state = {
      players: []
    }
  }

  componentDidMount() {
    fetch(`${process.env.REACT_APP_API_URL}get_players`).then(
      response => response.json()
    ).then(
      data => this.setState({players: data.result})
    )
  }

  render () {
    const {onPlayerSelected} = this.props

    return <MaterialTable
    
      columns={[
        { title: "Player", field: "name" },
        { title: "SteamID", field: "steam_id_64" },
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
  }
}


const CompactList = ({players, classes, handleToggle}) => (
  <List className={classes.root}>
  {players.map(value => {
    const labelId = `checkbox-list-label-${value.name}`;

    return (
      <ListItem key={value.name} role={undefined} dense button onClick={(value) => handleToggle(value)}>
        <ListItemIcon>
          <Checkbox
            edge="start"
            checked={false}
            tabIndex={-1}
            disableRipple
            inputProps={{ 'aria-labelledby': labelId }}
          />
        </ListItemIcon>
        <ListItemText id={labelId} primary={value.name} secondary={value.steam_id_64}/>
        <ListItemSecondaryAction>
          <PlayerActions size="small" />
        </ListItemSecondaryAction>
      </ListItem>
    );
  })}
</List>
)

const SelectedPlayers = ({players}) => (
  <React.Fragment>
    { players.map((p) => (
      <Chip label={p.name} />
      )
    )}
  </React.Fragment>
)

const PlayerActions = ({size}) => {
  const classes = useStyles();

  return <React.Fragment>
    <ButtonGroup size={size} aria-label="small outlined button group">
    <Button>
      PUNISH
    </Button>
    <Button>
      KICK
    </Button>
    <Button>
      2H BAN
    </Button>
    <Button>
      PERMA BAN
    </Button>
    </ButtonGroup>
  </React.Fragment>
}

class PlayerView extends Component {
  constructor(props) {
    super()
    this.state = {
      selectedPlayers: [],
      players: [],
      filter: null
    }

    this.onPlayerSelected = this.onPlayerSelected.bind(this)
    this.filterPlayers = this.filterPlayers.bind(this)
    this.filterChange = this.filterChange.bind(this)
  }

  onPlayerSelected(players) {
    console.log(players)
    this.setState({selectedPlayers: players})
  }

  componentDidMount() {
    fetch(`${process.env.REACT_APP_API_URL}get_players`).then(
      response => response.json()
    ).then(
      data => this.setState({players: data.result})
    )
  }

  filterChange(regex) {
      this.setState({filter: regex})
  }

  filterPlayers(players, regex) {
    console.log(regex)
    if (!regex) {
      return players
    }
    const res = _.filter(players, (p) => p.name.toLowerCase().indexOf(regex) >= 0 )
    console.log(res)
    return res
  }

  render() {
    const {classes} = this.props 
    const {selectedPlayers, players, filter} = this.state

    return <Grid container spacing={3}>
      <Grid item xs={6}>
        {/* <PlayerList onPlayerSelected={this.onPlayerSelected} /> */}
        <Filter handleChange={this.filterChange} />
        {
          players
          ? <CompactList classes={classes} players={this.filterPlayers(players, filter)}/>
          : "No players to list"
        }
      </Grid>
      <Grid item xs={6}>
        <Paper className={classes.paper}>
          <SelectedPlayers players={selectedPlayers} />
          <PlayerActions players={selectedPlayers}/>
        </Paper>
      </Grid>
    </Grid> 
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
