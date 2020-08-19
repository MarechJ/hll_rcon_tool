import React, { Component } from "react";
import List from "@material-ui/core/List";
import { Grid } from "@material-ui/core";
import ListItem from "@material-ui/core/ListItem";
import ListItemSecondaryAction from "@material-ui/core/ListItemSecondaryAction";
import ListItemText from "@material-ui/core/ListItemText";
import _ from "lodash";
import "react-toastify/dist/ReactToastify.css";
import { PlayerActions } from "./playerActions";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faLock,
  faQuestionCircle,
  faExclamationCircle,
} from "@fortawesome/free-solid-svg-icons";
import { faSteam } from "@fortawesome/free-brands-svg-icons";
import Link from "@material-ui/core/Link";
import withWidth from "@material-ui/core/withWidth";
import Icon from "@material-ui/core/Icon";
import OpenInNewIcon from "@material-ui/icons/OpenInNew";
import { getEmojiFlag } from "../../utils/emoji";
import { Map, List as IList } from "immutable";
import ScheduleIcon from "@material-ui/icons/Schedule";
import { Emoji } from "emoji-mart";
import LockIcon from "@material-ui/icons/Lock";
import { getName } from "country-list";
import Popover from "@material-ui/core/Popover";
import Typography from "@material-ui/core/Typography";
import { makeStyles } from "@material-ui/core/styles";
import { join } from "lodash/array";
import moment from "moment";

const zeroPad = (num, places) => String(num).padStart(places, "0");

const useStyles = makeStyles((theme) => ({
  popover: {
    pointerEvents: "none",
  },
  paper: {
    padding: theme.spacing(1),
  },
}));

function WithPopOver(props) {
  const classes = useStyles();
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handlePopoverOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handlePopoverClose = () => {
    setAnchorEl(null);
  };

  const open = Boolean(anchorEl);

  return (
    <React.Fragment>
      <Typography
        style={{ display: "inline" }}
        aria-owns={open ? "mouse-over-popover" : undefined}
        aria-haspopup="true"
        onMouseEnter={handlePopoverOpen}
        onMouseLeave={handlePopoverClose}
      >
        {props.children}
      </Typography>
      <Popover
        id="mouse-over-popover"
        className={classes.popover}
        classes={{
          paper: classes.paper,
        }}
        open={open}
        anchorEl={anchorEl}
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "left",
        }}
        transformOrigin={{
          vertical: "top",
          horizontal: "left",
        }}
        onClose={handlePopoverClose}
        disableRestoreFocus
      >
        <Typography>{props.content}</Typography>
      </Popover>
    </React.Fragment>
  );
}

function seconds_to_time(seconds) {
  const hours = Math.trunc(seconds / 60 / 60);
  const minutes = Math.trunc(seconds / 60 - hours * 60);

  return `${zeroPad(hours, 2)}:${zeroPad(minutes, 2)}`;
}

const getCountry = (profile) => {
  const country = profile.get("country");

  if (country == "private") {
    return (
      <WithPopOver content="Account is private">
        <FontAwesomeIcon icon={faLock} />
      </WithPopOver>
    );
  }
  if (country === "") {
    return (
      <WithPopOver content="No country specified">
        <FontAwesomeIcon icon={faQuestionCircle} />
      </WithPopOver>
    );
  }
  return (
    <img
      alt={country}
      title={country ? getName(country) : ''}
      style={{ height: "12px" }}
      src={`http://catamphetamine.gitlab.io/country-flag-icons/3x2/${country}.svg`}
    />
  );
};

const getBans = (profile) => {
  console.log(profile)
  return profile.get("steam_bans", {}) && profile.get("steam_bans", {}).get('has_bans') === true ? (
    <WithPopOver
      content={`Players has bans: ${JSON.stringify(profile.get("steam_bans"))}`}
    >
      <FontAwesomeIcon color="red" icon={faExclamationCircle} />
    </WithPopOver>
  ) : (
    ""
  )
  }

const Flag = ({ data, onDeleteFlag }) => (
  <Link
    onClick={() =>
      window.confirm("Delete flag?") ? onDeleteFlag(data.get("id")) : ""
    }
  >
    <WithPopOver content={`Comment: ${data.get("comment")}`}>
      {getEmojiFlag(data.get("flag"), 22)}
    </WithPopOver>
  </Link>
);

const formatPunitions = (profile) => {
  const formatTime = (item) => item.get("time");
  const lines = profile
    .get("received_actions", [])
    .map((item) => `${formatTime(item)} ${item.get('action_type')} by ${item.get('by')}: ${item.get('reason')}`);
  console.log(lines);
  return <pre>{lines.join("\n")}</pre>;
};

const PlayerItem = ({
  classes,
  name,
  steamID64,
  profile,
  handleAction,
  nbButtons,
  onFlag,
  onDeleteFlag,
}) => (
  <ListItem key={name} dense>
    <ListItemText
      id={`checkbox-list-label-${steamID64}`}
      primary={
        <React.Fragment>
          <WithPopOver content={formatPunitions(profile)}>{name}</WithPopOver>
          {" - "}
          {getCountry(profile)}
          {" - "}
          <Link
            className={classes.marginRight}
            target="_blank"
            color="inherit"
            href={`https://steamcommunity.com/profiles/${steamID64}`}
          >
            <FontAwesomeIcon icon={faSteam} />
          </Link>
        </React.Fragment>
      }
      secondary={
        <React.Fragment>
          <span>
            {seconds_to_time(profile.get("current_playtime_seconds"))} - #
            {profile.get("sessions_count")} - {getBans(profile)}
          </span>{" "}
          <Link
            target="_blank"
            color="inherit"
            href={`${process.env.REACT_APP_API_URL}player?steam_id_64=${steamID64}`}
          >
            {steamID64} <Icon component={OpenInNewIcon} fontSize="inherit" />
          </Link>
          <p className={classes.noPaddingMargin}>
            {profile.get("flags", []).map((d) => (
              <Flag data={d} onDeleteFlag={onDeleteFlag} />
            ))}
          </p>
        </React.Fragment>
      }
    />
    <ListItemSecondaryAction>
      <PlayerActions
        size="small"
        handleAction={handleAction}
        onFlag={onFlag}
        displayCount={nbButtons}
        penaltyCount={profile.get("penalty_count", Map())}
      />
    </ListItemSecondaryAction>
  </ListItem>
);

class CompactList extends React.Component {
  render() {
    const {
      playerNames,
      playerSteamIDs,
      playerProfiles,
      classes,
      handleAction,
      alphaSort,
      width,
      onFlag,
      onDeleteFlag,
    } = this.props;
    let players = _.zip(playerNames, playerSteamIDs, playerProfiles);
    if (alphaSort === true) {
      players = _.sortBy(players, (p) => p[0].toLowerCase());
    }

    const sizes = {
      xs: 0,
      sm: 3,
      md: 1,
      lg: 4,
      xl: 10,
    };

    return (
      <List className={classes.root}>
        {players.map((player) => (
          <PlayerItem
            classes={classes}
            nbButtons={sizes[width]}
            name={player[0]}
            steamID64={player[1]}
            key={player[1]}
            profile={player[2]}
            handleAction={(actionType) => handleAction(actionType, player[0])}
            onFlag={() =>
              onFlag(
                Map({
                  steam_id_64: player[2].get("steam_id_64", player[1]),
                  names: player[2].get(
                    "names",
                    IList([Map({ name: player[0] })])
                  ),
                })
              )
            }
            onDeleteFlag={onDeleteFlag}
          />
        ))}
      </List>
    );
  }
}

export default withWidth()(CompactList);
