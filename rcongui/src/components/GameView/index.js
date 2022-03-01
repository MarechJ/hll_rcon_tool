import React from "react";
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
  Checkbox
} from "@material-ui/core";
import { fromJS } from "immutable";
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
import { PlayerItem } from '../PlayerView/playerList'

const useStyles = makeStyles((theme) => ({
  root: {
  
    backgroundColor: theme.palette.background.paper,
  },
  nested: {
    paddingLeft: theme.spacing(4),
  },
  small: {
    width: theme.spacing(3),
    height: theme.spacing(3),
  },
}));


const samplePLayer = fromJS({
  "name": "Noperator",
  "steam_id_64": "76561199137886650",
  "country": "private",
  "steam_bans": {
    "SteamId": "76561199137886650",
    "CommunityBanned": false,
    "VACBanned": false,
    "NumberOfVACBans": 0,
    "DaysSinceLastBan": 0,
    "NumberOfGameBans": 0,
    "EconomyBan": "none",
    "has_bans": false
  },
  "profile": {
    "id": 34463,
    "steam_id_64": "76561199137886650",
    "created": "2021-02-06T20:30:52.757",
    "names": [
      {
        "id": 72789,
        "name": "Noperator",
        "steam_id_64": "76561199137886650",
        "created": "2021-05-04T22:08:13.329",
        "last_seen": "2022-02-28T15:22:53.242"
      },
      {
        "id": 35561,
        "name": "Notperator",
        "steam_id_64": "76561199137886650",
        "created": "2021-02-06T20:30:52.776",
        "last_seen": "2021-02-15T13:20:57"
      }
    ],
    "sessions": [
      {
        "id": 596581,
        "steam_id_64": "76561199137886650",
        "start": "2022-02-28T15:22:47",
        "end": null,
        "created": "2022-02-28T15:22:51.856"
      }
    ],
    "sessions_count": 23,
    "total_playtime_seconds": 102960,
    "current_playtime_seconds": 11779,
    "received_actions": [
      {
        "action_type": "KICK",
        "reason": "Teamkilling",
        "by": "Heavenly",
        "time": "2021-08-12T01:08:51.443"
      }
    ],
    "penalty_count": {
      "PERMABAN": 0,
      "TEMPBAN": 0,
      "PUNISH": 0,
      "KICK": 1
    },
    "blacklist": null,
    "flags": [],
    "watchlist": null,
    "steaminfo": {
      "id": 45436,
      "created": "2021-03-24T02:18:12.490",
      "updated": null,
      "profile": {
        "avatar": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/04/048a8f3b3c485ef56de940d94d7da0abc96758b6.jpg",
        "steamid": "76561199137886650",
        "avatarfull": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/04/048a8f3b3c485ef56de940d94d7da0abc96758b6_full.jpg",
        "avatarhash": "048a8f3b3c485ef56de940d94d7da0abc96758b6",
        "profileurl": "https://steamcommunity.com/profiles/76561199137886650/",
        "personaname": "Noperator",
        "avatarmedium": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/04/048a8f3b3c485ef56de940d94d7da0abc96758b6_medium.jpg",
        "personastate": 0,
        "profilestate": 1,
        "communityvisibilitystate": 2
      },
      "country": null,
      "bans": null
    }
  },
  "is_vip": false
})

const PlayerInfo = ({ classes: globalClasses }) => {

}

const GameView = ({ classes: globalClasses }) => {
  const classes = useStyles();
  const [open, setOpen] = React.useState(true);

  const handleClick = () => {
    setOpen(!open);
  };

  return <Grid container>
    <Grid item xs={12} md={6}>
      <List
        dense
        component="nav"
        aria-labelledby="nested-list-subheader"
        subheader={
          <ListSubheader component="div" id="nested-list-subheader">
            Nested List Items
          </ListSubheader>
        }
        className={classes.root}
      >
        <ListItem button onClick={handleClick}>
          <ListItemIcon>
            <Avatar className={classes.small}>
              A
            </Avatar>
          </ListItemIcon>
          <ListItemText primary="Able" />
          <ListItemSecondaryAction>
            <Checkbox
              edge="end"
            />
          </ListItemSecondaryAction>

        </ListItem>
        <Collapse in={open} timeout="auto" unmountOnExit>
          <List component="div" disablePadding>
            <PlayerItem 
              classes={globalClasses} 
              player={samplePLayer} 
              onDeleteFlag={() => (null)}
            />
             <PlayerItem 
              classes={globalClasses} 
              player={samplePLayer} 
              onDeleteFlag={() => (null)}
            />
          </List>
        </Collapse>
      </List>

    </Grid>
    <Grid item xs={12} md={6}>Team 2</Grid>
  </Grid>
}

export default GameView;