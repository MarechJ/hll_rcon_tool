import {
  Avatar,
  Typography,
  Link,
  ListItem,
  ListItemAvatar,
  ListItemText,
  IconButton,
} from "@material-ui/core";
import React from "react";
import { List, Map } from "immutable";
import Tooltip from "@material-ui/core/Tooltip";
import FileCopyIcon from "@material-ui/icons/FileCopy";
import AnnouncementIcon from "@material-ui/icons/Announcement";
import ListItemSecondaryAction from "@material-ui/core/ListItemSecondaryAction";
import KeyboardArrowUpIcon from "@material-ui/icons/KeyboardArrowUp";
import KeyboardArrowDownIcon from "@material-ui/icons/KeyboardArrowDown";
import {pure} from "recompose";
import {getName} from "country-list";

const getCountry = (country) => {
  if (country === "" || country === null) {
    return ""
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

export const PlayerHeader = pure(({ classes, player }) => {
  const [showAll, setShowAll] = React.useState(false);
  const hasMultipleName = player.get("names") && player.get("names").size > 1;

  const playerNames = player.get("names", null) ? player.get("names") : new List();
  const firstName = playerNames.get(0, null) ? playerNames.get(0) : new Map()
  const firstNameLetter = firstName.get("name", "?")[0]
  const namesByMatch = player.get("names_by_match", null) ? player.get("names_by_match") : new List()
  const steamProfile = player.get('steaminfo') ? player.get("steaminfo").get("profile") : new Map()
  const avatarUrl = steamProfile ? steamProfile.get("avatar", null) : null
  const country = player.get('steaminfo') ? player.get('steaminfo').get("country", "") : ""

  return (
    <ListItem alignItems="flex-start">
      <ListItemAvatar>
        <Link
          target="_blank"
          color="inherit"
          href={`https://steamcommunity.com/profiles/${player.get(
            "steam_id_64"
          )}`}
        >
          <Avatar src={avatarUrl}>
            {firstNameLetter}
          </Avatar>
        </Link>
      </ListItemAvatar>
      <ListItemText
        primary={
          <React.Fragment>
            {showAll ? (
              <Typography variant="body1">
                {hasMultipleName ? (
                  <IconButton
                    size="small"
                    color="primary"
                    onClick={() => setShowAll(false)}
                  >
                    <KeyboardArrowUpIcon fontSize="inherit" />
                  </IconButton>
                ) : (
                    ""
                  )}
                {playerNames
                  .map((n) => n.get("name"))
                  .join(" | ")}
              </Typography>
            ) : (
                <Typography variant="body1">
                  {hasMultipleName ? (
                    <IconButton
                      size="small"
                      color="primary"
                      onClick={() => setShowAll(true)}
                    >
                      <KeyboardArrowDownIcon fontSize="inherit" />
                    </IconButton>
                  ) : (
                      ""
                    )}
                  {namesByMatch.get(0, "")}  {getCountry(country)}
                </Typography>
              )}
          </React.Fragment>
        }
        secondary={
          <Link
            target="_blank"
            color="inherit"
            href={`${process.env.REACT_APP_API_URL}player?steam_id_64=${player.get("steam_id_64")}`}
          >
            {player.get("steam_id_64")}
          </Link>
        }
      />
      <ListItemSecondaryAction>
        <Tooltip title="Copy steam id to clipboard">
          <Typography variant="body2">
            <FileCopyIcon
              fontSize="small"
              size="small"
              style={{ cursor: "pointer" }}
              onClick={() => {
                if (navigator.clipboard === undefined) {
                  alert("This feature only works if your rcon uses HTTPS");
                  return;
                }
                var text = player.get("steam_id_64");
                navigator.clipboard.writeText(text).then(
                  function () {
                    console.log("Async: Copying to clipboard was successful!");
                  },
                  function (err) {
                    console.error("Async: Could not copy text: ", err);
                  }
                );
              }}
            />
          </Typography>
        </Tooltip>
        <Tooltip title="Copy report template to clipboard">
          <Typography variant="body2">
            <AnnouncementIcon
              fontSize="small"
              size="small"
              style={{ cursor: "pointer" }}
              onClick={() => {
                var text = `Name: ${player
                  .get("names")
                  .first()
                  .get("name")}\nAliases: ${player
                    .get("names", new List())
                    .map((n) => n.get("name"))
                    .join(" | ")}\nSteamID: ${player.get(
                      "steam_id_64"
                    )}\nSteam URL: https://steamcommunity.com/profiles/${player.get(
                      "steam_id_64"
                    )}\nType of issue:\nDescription:\nEvidence:`;
                if (navigator.clipboard === undefined) {
                  alert(`This feature only works if your rcon uses HTTPS.`);
                  return;
                }
                if (navigator.clipboard === undefined) {
                } else {
                  navigator.clipboard.writeText(text).then(
                    function () {
                      console.log(
                        "Async: Copying to clipboard was successful!"
                      );
                    },
                    function (err) {
                      console.error("Async: Could not copy text: ", err);
                    }
                  );
                }
              }}
            />
          </Typography>
        </Tooltip>
      </ListItemSecondaryAction>
    </ListItem>
  );
});
