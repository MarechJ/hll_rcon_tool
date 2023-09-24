import React from "react";
import { Set } from "immutable";
import {
  Grid,
  Link,
  Avatar,
  List,
  ListItem,
  ListItemSecondaryAction,
  ListItemAvatar,
  ListItemText,
  Typography,
  Paper,
  IconButton,
} from "@material-ui/core";
import CancelIcon from "@material-ui/icons/Cancel";
import { pure } from "recompose";
import { safeGetSteamProfile } from "./Scores";
import { SubList } from "./SubList";
import makeSteamProfileUrl from "../../utils/makeSteamProfileUrl";

export const PlayerStatProfile = pure(({ playerScore, onClose }) => {
  const steamProfile = safeGetSteamProfile(playerScore);
  const excludedKeys = new Set([
    "player_id",
    "id",
    "steaminfo",
    "map_id",
    "most_killed",
    "weapons",
    "death_by",
    "death_by_weapons",
  ]);

  return (
    <Grid item xs={12}>
      <Grid container justify="center">
        <Grid item xs={12} md={6} lg={4} xl={2}>
          <Paper>
            <List>
              <ListItem divider>
                <ListItemAvatar>
                  <Avatar src={steamProfile.get("avatar")}></Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={
                    <Typography variant="h4">
                      <Link
                        color="inherit"
                        href={
                          steamProfile.get("profileurl") ||
                          makeSteamProfileUrl(playerScore.get("steam_id_64"))
                        }
                        target="_blank"
                      >
                        {playerScore.get("player") ||
                          steamProfile.get("personaname")}
                      </Link>
                    </Typography>
                  }
                />
                <ListItemSecondaryAction>
                  <IconButton onClick={onClose}>
                    <CancelIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
              <SubList
                playerScore={playerScore}
                dataMapKey="weapons"
                title="Kills by weapons"
                subtitle="'None' means Tank, Arty, roadkill or some explosives"
                openDefault
              />
              <SubList
                playerScore={playerScore}
                dataMapKey="death_by_weapons"
                subtitle="'None' means Tank, Arty, roadkill or some explosives"
                title="Deaths by weapons"
              />
              <SubList
                playerScore={playerScore}
                dataMapKey="most_killed"
                title="Kills by player"
              />
              <SubList
                playerScore={playerScore}
                dataMapKey="death_by"
                title="Deaths by player"
              />
              <SubList
                playerScore={playerScore.filterNot((v, k) =>
                  excludedKeys.has(k)
                )}
                title="Raw stats"
                sortByKey
              />
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Grid>
  );
});
