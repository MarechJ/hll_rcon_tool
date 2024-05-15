import React from "react";
import { Chip, Grid, Typography } from "@material-ui/core";

export function PlayerVipSummary({ player, isVip }) {
  const playerNames =
    player && player.get("names")
      ? player.get("names").map((name) => <Chip label={name.get("name")} />)
      : "No name recorded";

  let vipExpirationTimestamp = "Not VIP";

  if (isVip) {
    vipExpirationTimestamp =
      player && player.get("vip_expiration")
        ? player.get("vip_expiration")
        : "Never";
  }

  return (
    <Grid container>
      <Grid item xs={12}>
        <Typography variant="body2">Name: {playerNames}</Typography>
      </Grid>
      <Grid item xs={12}>
        <Typography>Player ID: {player && player.get("player_id")}</Typography>
      </Grid>
      <Grid item xs={12}>
        <Typography>
          Current VIP Expiration: {vipExpirationTimestamp}
        </Typography>
      </Grid>
    </Grid>
  );
}
