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

const ColorButton = withStyles(theme => ({
  root: {
    color: theme.palette.getContrastText(yellow[500]),
    backgroundColor: yellow[500],
    '&:hover': {
      backgroundColor: yellow[700],
    },
  },
}))(Button);

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

const SelectedPlayers = ({players}) => (
  <React.Fragment>
    { players.map((p) => (
      <Chip label={p.name} />
      )
    )}
  </React.Fragment>
)

const PlayerActions = () => {
  const classes = useStyles();

  return <React.Fragment>
    <Button variant="contained" className={classes.margin}>
      PUNISH
    </Button>
    <Button variant="contained" color="primary" className={classes.margin}>
      KICK
    </Button>
    <ColorButton variant="contained" color="primary" className={classes.margin}>
      2H BAN
    </ColorButton>
    <Button variant="contained" color="secondary" className={classes.margin}>
      PERMA BAN
    </Button>
  </React.Fragment>
}

class PlayerView extends Component {
  constructor(props) {
    super()
    this.state = {
      selectedPlayers: []
    }

    this.onPlayerSelected = this.onPlayerSelected.bind(this)
  }

  onPlayerSelected(players) {
    console.log(players)
    this.setState({selectedPlayers: players})
  }

  render() {
    const {classes} = this.props 
    const {selectedPlayers} = this.state

    return <Grid container spacing={3}>
      <Grid item xs={6}>
        <PlayerList onPlayerSelected={this.onPlayerSelected} />
      </Grid>
      <Grid item xs={6}>
        <Paper className={classes.paper}>
          <SelectedPlayers players={selectedPlayers} />
          <PlayerActions />
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
