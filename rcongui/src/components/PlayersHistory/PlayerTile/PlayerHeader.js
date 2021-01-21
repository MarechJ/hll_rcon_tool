import {
  Avatar,
  Grid,
  Typography,
  Link,
  ListItem,
  ListItemAvatar,
  ListItemText,
} from "@material-ui/core";
import React from "react";
import { List } from "immutable";
import Tooltip from "@material-ui/core/Tooltip";
import FileCopyIcon from "@material-ui/icons/FileCopy";
import AnnouncementIcon from "@material-ui/icons/Announcement";

export const PlayerHeader = ({ classes, player }) => (
  <ListItem alignItems="flex-start">
    <ListItemAvatar>
      <Avatar>{player
        .get("names", new List()).get(0, "?")[0]}</Avatar>
    </ListItemAvatar>
    <ListItemText 
      
      primary={player
        .get("names", new List())
        .map((n) => n.get("name"))
        .join(" - ")}
      secondary={
        <React.Fragment>
          <Typography
            component="span"
            variant="body2"
            className={classes.inline}
            color="textPrimary"
          >
            Ali Connors
          </Typography>
          {" — I'll be in your neighborhood doing errands this…"}
        </React.Fragment>
      }
    />
  </ListItem>
);

const OldPlayerHeader = ({ classes, player }) => {
  return (
    <Grid container spacing={1} alignItems="center" justify="flex-start">
      <Grid item>
        <Avatar>A</Avatar>
      </Grid>
      <Grid item xs={10}>
        <Grid
          container
          alignContent="stretch"
          alignItems="stretch"
          justify="space-between"
        >
          <Grid item={12}>
            <Typography variant="subtitle1" className={classes.ellipsis}>
              {player
                .get("names", new List())
                .map((n) => n.get("name"))
                .join(" - ")}
            </Typography>
          </Grid>
          <Grid item={6}>
            <Link
              target="_blank"
              color="inherit"
              href={`${
                process.env.REACT_APP_API_URL
              }player?steam_id_64=${player.get("steam_id_64")}`}
            >
              <Typography
                align="left"
                variant="body2"
                id={`id_link_${player.get("steam_id_64")}`}
              >
                {player.get("steam_id_64")}
              </Typography>
            </Link>
          </Grid>
          <Grid item={6}>
            <Grid container spacing={1}>
              <Grid item>
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
                            console.log(
                              "Async: Copying to clipboard was successful!"
                            );
                          },
                          function (err) {
                            console.error("Async: Could not copy text: ", err);
                          }
                        );
                      }}
                    />
                  </Typography>
                </Tooltip>
              </Grid>
              <Grid item>
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
                          .get("name")}\nSteamID: ${player.get(
                          "steam_id_64"
                        )}\nSteam URL: https://steamcommunity.com/profiles/${player.get(
                          "steam_id_64"
                        )}\nType of issue:\nDescription:\nEvidence:`;

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
                      }}
                    />
                  </Typography>
                </Tooltip>
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </Grid>
  );
};
