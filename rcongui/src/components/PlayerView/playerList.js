import React, { Component } from "react";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemSecondaryAction from "@material-ui/core/ListItemSecondaryAction";
import ListItemText from "@material-ui/core/ListItemText";
import _ from "lodash";
import "react-toastify/dist/ReactToastify.css";
import { PlayerActions } from "./playerActions";

const PlayerItem = ({ name, steamID64, handleAction }) => (
  <ListItem key={name} role={undefined} dense>
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
    if (nextProps.playerSteamIDs.length !== this.props.playerSteamIDs.length 
      || nextProps.alphaSort !== this.props.alphaSort) {
      return true;
    }
    const diff = _.difference(
      nextProps.playerSteamIDs,
      this.props.playerSteamIDs
    );
    return diff.length > 0;
  }

  render() {
    const { playerNames, playerSteamIDs, classes, handleAction, alphaSort } = this.props;
    let players = _.zip(playerNames, playerSteamIDs); 
    if (alphaSort === true) {
      players = _.sortBy(players, (p) => p[0].toLowerCase())
    }
    return (
      <List className={classes.root}>
        {players.map(player => (
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

export default CompactList;
