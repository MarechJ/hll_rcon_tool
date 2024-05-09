import React from "react";
import { Grid, Typography } from "@material-ui/core";
import { fromJS } from "immutable";
import { reduce } from "lodash";

export function banListFromServer(data) {
  // console.log(`banListFromServer ${JSON.stringify(data)}`)
  return fromJS(
    reduce(
      data,
      (acc, val) => {
        if (!acc.hasOwnProperty(val.player_id)) {
          acc[val.player_id] = new Array(val);
        } else {
          acc[val.player_id].push(val);
        }
        return acc;
      },
      {}
    )
  );
}

export const PlayerBan = ({ classes, bans, player }) => {
  const playerBans = bans.get(player.get("steam_id_64"));
  const formattedBans = {};

  playerBans?.forEach((b) =>
    b.get("type") === "temp"
      ? (formattedBans.temp = "IS TEMP BANNED")
      : (formattedBans.perma = "IS PERMA BANNED")
  );
  return (
    <Grid
      container
      justify="space-between"
      spacing={0}
      className={classes.noPaddingMargin}
    >
      <Grid item xs={6}>
        {formattedBans.temp ? (
          <Typography variant="h7" color="secondary">
            {formattedBans.temp}
          </Typography>
        ) : (
          ""
        )}
      </Grid>
      <Grid item xs={6}>
        {formattedBans.perma ? (
          <Typography variant="h7" color="secondary">
            {formattedBans.perma}
          </Typography>
        ) : (
          ""
        )}
      </Grid>
    </Grid>
  );
};
