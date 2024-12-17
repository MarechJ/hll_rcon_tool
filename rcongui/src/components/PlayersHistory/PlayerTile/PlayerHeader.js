import {
  Avatar,
  IconButton,
  Link,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Typography,
} from "@mui/material";
import { Link as RouterLink } from "react-router-dom";
import { List, Map } from "immutable";
import Tooltip from "@mui/material/Tooltip";
import FileCopyIcon from "@mui/icons-material/FileCopy";
import AnnouncementIcon from "@mui/icons-material/Announcement";
import ListItemSecondaryAction from "@mui/material/ListItemSecondaryAction";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import { getName } from "country-list";
import makePlayerProfileUrl from "../../../utils/makePlayerProfileUrl";
import {Fragment, useState} from "react";

export const getCountry = (country) => {
  if (country === "" || country === null) {
    return "";
  }
  return (
    <img
      alt={country}
      title={country ? getName(country) : ""}
      style={{ height: "12px" }}
      src={`https://catamphetamine.gitlab.io/country-flag-icons/3x2/${country}.svg`}
    />
  );
};

export const PlayerHeader = ({ player }) => {
  const [showAll, setShowAll] = useState(false);
  const hasMultipleName = player.get("names") && player.get("names").size > 1;

  const playerNames = player.get("names", null)
    ? player.get("names")
    : new List();
  const firstName = playerNames.get(0, null) ? playerNames.get(0) : new Map();
  const firstNameLetter = firstName.get("name", "?")[0];
  const namesByMatch = player.get("names_by_match", null)
    ? player.get("names_by_match")
    : new List();
  const steamProfile = player.get("steaminfo")
    ? player.get("steaminfo").get("profile")
    : new Map();
  const avatarUrl = steamProfile ? steamProfile.get("avatar", null) : null;
  const country = player.get("steaminfo")
    ? player.get("steaminfo").get("country", "")
    : "";

  return (
    <ListItem alignItems="flex-start">
      <ListItemAvatar>
        <Link
          target="_blank"
          color="inherit"
          href={makePlayerProfileUrl(
            player.get("player_id"),
            firstName.get("name")
          )}
        >
          <Avatar src={avatarUrl}>{firstNameLetter}</Avatar>
        </Link>
      </ListItemAvatar>
      <ListItemText
        primary={
          <Fragment>
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
                {playerNames.map((n) => n.get("name")).join(" | ")}
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
                {namesByMatch.get(0, firstName?.get("name"))} {getCountry(country)}
              </Typography>
            )}
          </Fragment>
        }
        secondary={
          <Link
            color="inherit"
            component={RouterLink}
            to={`/records/players/${player.get("player_id")}`}
          >
            {player.get("player_id")}
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
                var text = player.get("player_id");
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
                    .join(" | ")}\nPlayer ID: ${player.get(
                      "player_id"
                    )}\nSteam URL: ${makePlayerProfileUrl(
                      player.get("player_id"),
                      player.get("names").first().get("name")
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
};
