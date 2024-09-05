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
  const playerBans = bans.get(player.get("player_id"));
  const formattedBans = [];
  
  if (player.get("is_blacklisted")) {
    formattedBans.push("IS BLACKLISTED");
  }
  playerBans?.forEach((b) =>
    b.get("type") === "temp"
      ? formattedBans.push("IS TEMPBANNED")
      : formattedBans.push("IS PERMABANNED")
  );
  return (
    <Grid
      container
      justify="space-between"
      spacing={0}
      className={classes.noPaddingMargin}
    >
      {formattedBans.map((formattedBan) => (
        <Grid item xs={6}>
          <Typography variant="h7" color="secondary">
            {formattedBan}
          </Typography>
        </Grid>
      ))}
    </Grid>
  );
};
