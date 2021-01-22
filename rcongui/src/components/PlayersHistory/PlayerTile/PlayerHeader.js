import {
  Avatar,
  Grid,
  Typography,
  Link,
  ListItem,
  ListItemAvatar,
  ListItemText,
  IconButton,
} from "@material-ui/core";
import React from "react";
import { List } from "immutable";
import Tooltip from "@material-ui/core/Tooltip";
import FileCopyIcon from "@material-ui/icons/FileCopy";
import AnnouncementIcon from "@material-ui/icons/Announcement";
import ListItemSecondaryAction from "@material-ui/core/ListItemSecondaryAction";
import KeyboardArrowUpIcon from "@material-ui/icons/KeyboardArrowUp";
import KeyboardArrowDownIcon from "@material-ui/icons/KeyboardArrowDown";
import { pure } from "recompose";

export const PlayerHeader = pure(({ classes, player }) => {
  const [showAll, setShowAll] = React.useState(false);
  const hasMultipleName = player.get("names") && player.get("names").size > 1;

  return (
    <ListItem alignItems="flex-start">
      <ListItemAvatar>
        <Avatar>
          {
            player
              .get("names", new List())
              .get(0, new Map())
              .get("name", "?")[0]
          }
        </Avatar>
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
                {player
                  .get("names", new List())
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
                {player.get("names_by_match", new List()).get(0, "")}
              </Typography>
            )}
          </React.Fragment>
        }
        secondary={player.get("steam_id_64")}
      />
      <ListItemSecondaryAction>
        <Tooltip title="Copy steam id to clipboard">
          <Typography variant="body2">
            <FileCopyIcon
              fontSize="small"
              size="small"
              style={{ cursor: "pointer" }}
              onClick={() => {
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
      </ListItemSecondaryAction>
    </ListItem>
  );
});
