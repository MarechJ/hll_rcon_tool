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

const zeroPad = (num, places) => String(num).padStart(places, "0");

function seconds_to_time(seconds) {
  const hours = Math.trunc(seconds / 60 / 60);
  const minutes = Math.trunc(seconds / 60 - hours * 60);

  return `${zeroPad(hours, 2)}:${zeroPad(minutes, 2)}`;
}

const getCountry = (profile) => {
  const country = profile.get("country");

  if (country == "private") {
    return <FontAwesomeIcon icon={faLock} />;
  }
  if (country === "") {
    return <FontAwesomeIcon icon={faQuestionCircle} />;
  }
  return (
    <img
      alt={country}
      title={getName(country)}
      style={{ height: "12px" }}
      src={`http://catamphetamine.gitlab.io/country-flag-icons/3x2/${country}.svg`}
    />
  );
};

const getBans = (profile) =>
  profile.get("has_steam_bans") ? (
    <React.Fragment><FontAwesomeIcon color="red" icon={faExclamationCircle} /> - </React.Fragment>
  ) : (
    ""
  );

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
          {name}{" "}
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
            {profile.get("sessions_count")} - {getCountry(profile)} -{" "}
            {getBans(profile)}
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
              <Link
                onClick={() =>
                  window.confirm("Delete flag?")
                    ? onDeleteFlag(d.get("id"))
                    : ""
                }
              >
                {getEmojiFlag(d.get("flag"), 22)}
              </Link>
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
