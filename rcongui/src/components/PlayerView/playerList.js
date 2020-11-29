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
  faStar,
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
import { sumBy } from "lodash/math";
import { toPairs } from "lodash/object";

//import StarIcon from '@material-ui/icons/Star';

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

const getCountry = (player) => {
  const country = player.get("country");

  if (country == "private") {
    return (
      <WithPopOver content="Account is private">
        <FontAwesomeIcon icon={faLock} />
      </WithPopOver>
    );
  }
  if (country === "" || country === null) {
    return (
      <WithPopOver content="No country specified">
        <FontAwesomeIcon icon={faQuestionCircle} />
      </WithPopOver>
    );
  }
  return (
    <img
      alt={country}
      title={country ? getName(country) : ""}
      style={{ height: "12px" }}
      src={ `https://catamphetamine.gitlab.io/country-flag-icons/3x2/${country}.svg`}
    />
  );
};

const getBans = (profile) => {
  return profile.get("steam_bans") &&
    profile.get("steam_bans").get("has_bans") === true ? (
    <WithPopOver
      content={`Players has bans: ${JSON.stringify(profile.get("steam_bans"))}`}
    >
      <FontAwesomeIcon color="red" icon={faExclamationCircle} />
    </WithPopOver>
  ) : (
    ""
  );
};

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
  return profile
    .get("received_actions", [])
    .map((item) => (
      <Typography display="block" variant="caption" key={item}>{`${formatTime(
        item
      )} ${item.get("action_type")} by ${item.get("by")}: ${item.get(
        "reason"
      )}`}</Typography>
    ));
};

const PlayerItem = ({
  classes,
  player,
  handleAction,
  nbButtons,
  onFlag,
  onDeleteFlag,
}) => {
  const profile = player.get("profile") ? player.get("profile") : new Map();
  const name = player.get("name");
  const steamID64 = player.get("steam_id_64");

  return (
    <ListItem key={name} dense>
      <ListItemText
        id={`checkbox-list-label-${steamID64}`}
        primary={
          <React.Fragment>
            <WithPopOver content={formatPunitions(profile)}>{name}</WithPopOver>
            {" - "}
            {getCountry(player)}
            {" - "}
            {player.get("is_vip") ? (
              <React.Fragment>
                <FontAwesomeIcon icon={faStar} />
                {" - "}
              </React.Fragment>
            ) : (
              ""
            )}
            <Link
              className={classes.marginRight}
              target="_blank"
              color="inherit"
              href={ `https://steamcommunity.com/profiles/${steamID64}`}
            >
              <FontAwesomeIcon icon={faSteam} />
            </Link>
          </React.Fragment>
        }
        secondary={
          <React.Fragment>
            <span>
              {seconds_to_time(profile.get("current_playtime_seconds"))} - #
              {profile.get("sessions_count")} - {getBans(player)}
            </span>{" "}
            <Link
              target="_blank"
              color="inherit"
              href={`${process.env.REACT_APP_API_URL}player?steam_id_64=${steamID64}`}
            >
              {steamID64} <Icon component={OpenInNewIcon} fontSize="inherit" />
            </Link>
            <div className={classes.noPaddingMargin}>
              {profile.get("flags", []).map((d) => (
                <Flag key={d} data={d} onDeleteFlag={onDeleteFlag} />
              ))}
            </div>
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
};

const weightedPenalities = (penaltiesMap) => {
  const weights = {
    PUNISH: 1,
    KICK: 4,
    TEMPBAN: 10,
    PERMABAN: 100,
  };
  const res = penaltiesMap.reduce(
    (sum, value, key) => sum + weights[key] * value,
    0
  );
  console.log("Weighted penalites", res);
  return res;
};

const getSortedPlayers = (players, sortType) => {
  let myPlayers = players;
  const [direction, type] = sortType.split("_");

  if (!sortType || sortType === "") {
    return myPlayers;
  }

  const sortFuncs = {
    alpha: (p) => p.get("name").toLowerCase(),
    time: (p) =>
      !p.get("profile") ? 0 : p.get("profile").get("current_playtime_seconds"),
    country: (p) => {
      const country = p.get("country");
      if (!country) {
        return "zzy";
      }
      if (country === "private") return "zzz";
      return country;
    },
    sessions: (p) =>
      !p.get("profile") ? 0 : p.get("profile").get("sessions_count"),
    penalties: (p) =>
      !p.get("profile")
        ? 0
        : weightedPenalities(p.get("profile").get("penalty_count")),
    vips: (p) => p.get("is_vip"),
  };

  myPlayers = myPlayers.sortBy(sortFuncs[type]);

  if (direction === "desc") {
    myPlayers = myPlayers.reverse();
  }

  return myPlayers;
};

class CompactList extends React.Component {
  render() {
    const {
      players,
      classes,
      handleAction,
      sortType,
      width,
      onFlag,
      onDeleteFlag,
    } = this.props;

    let myPlayers = players;
    try {
      myPlayers = getSortedPlayers(players, sortType);
    } catch (err) {
      console.log("Unable to sort ", err);
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
        {myPlayers.map((player) => (
          <PlayerItem
            classes={classes}
            nbButtons={sizes[width]}
            player={player}
            key={player.get("steam_id_64")}
            handleAction={(actionType) =>
              handleAction(actionType, player.get("name"))
            }
            onFlag={() =>
              onFlag(
                Map({
                  steam_id_64: player.get("steam_id_64"),
                  names: (player.get("profile")
                    ? player.get("profile")
                    : new Map()
                  ).get("names", IList([Map({ name: player.get("name") })])),
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
