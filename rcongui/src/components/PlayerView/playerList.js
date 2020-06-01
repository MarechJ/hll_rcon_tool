import React, { Component } from "react";
import List from "@material-ui/core/List";
import { Grid } from '@material-ui/core'
import ListItem from "@material-ui/core/ListItem";
import ListItemSecondaryAction from "@material-ui/core/ListItemSecondaryAction";
import ListItemText from "@material-ui/core/ListItemText";
import _ from "lodash";
import "react-toastify/dist/ReactToastify.css";
import { PlayerActions } from "./playerActions";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSteam } from '@fortawesome/free-brands-svg-icons'
import Link from '@material-ui/core/Link';
import withWidth from "@material-ui/core/withWidth";
import Icon from '@material-ui/core/Icon';
import OpenInNewIcon from '@material-ui/icons/OpenInNew';
import { getEmojiFlag } from '../../utils/emoji'
import { Map } from 'immutable'


const PlayerItem = ({ classes, name, steamID64, profile, handleAction, nbButtons, onFlag, onDeleteFlag }) => (
  <ListItem key={name} dense>
    <ListItemText
      id={`checkbox-list-label-${steamID64}`}
      primary={name}
      secondary={
        <React.Fragment>
          <Link target="_blank" color="inherit" href={`${process.env.REACT_APP_API_URL}player?steam_id_64=${steamID64}`}>
            {steamID64} <Icon component={OpenInNewIcon} fontSize="inherit" />
          </Link>
          <p className={classes.noPaddingMargin}>
             {profile.get('flags', []).map(d =>
                <Link onClick={() => window.confirm("Delete flag?") ? onDeleteFlag(d.get('id')) : ''}>{getEmojiFlag(d.get('flag'))}</Link>
              )}
            
          </p>
        </React.Fragment>
      }
    />
    <ListItemSecondaryAction>
      <Link className={classes.marginRight} target="_blank" color="inherit" href={`https://steamcommunity.com/profiles/${steamID64}`}>
        <FontAwesomeIcon icon={faSteam} /></Link>
      <PlayerActions size="small" handleAction={handleAction} onFlag={onFlag} displayCount={nbButtons} penaltyCount={profile.get('penalty_count', Map())}  />
    </ListItemSecondaryAction>
  </ListItem>
);


class CompactList extends React.Component {
  render() {
    const { playerNames, playerSteamIDs, playerProfiles, classes, handleAction, alphaSort, width, onFlag, onDeleteFlag } = this.props;
    let players = _.zip(playerNames, playerSteamIDs, playerProfiles);
    if (alphaSort === true) {
      players = _.sortBy(players, (p) => p[0].toLowerCase())
    }

    return (
      <List className={classes.root}>
        {players.map(player => (
          <PlayerItem
            classes={classes}
            nbButtons={width === 'xs' ? 1 : width === 'xl' ? 10 : 4}
            name={player[0]}
            steamID64={player[1]}
            key={player[1]}
            profile={player[2]}
            handleAction={actionType => handleAction(actionType, player[0])}
            onFlag={() => onFlag(player[2])}
            onDeleteFlag={onDeleteFlag}
          />
        ))}
      </List>
    );
  }
}

export default withWidth()(CompactList);
