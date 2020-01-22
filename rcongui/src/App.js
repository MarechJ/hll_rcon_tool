import React, {Component} from 'react';
import MaterialTable from "material-table";
import './App.css';
import { throwStatement } from '@babel/types';

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
    console.log(this.state.players)
    return <MaterialTable
      columns={[
        { title: "Player", field: "name" },
        { title: "SteamID", field: "steam_id_64" },
      ]}
      data={this.state.players}
      title="Player List"
    />
  }
}

function App() {
  return (
      <div className="App" style={{ maxWidth: "100%" }}>
       <PlayerList />
      </div>
  );
}

export default App;
