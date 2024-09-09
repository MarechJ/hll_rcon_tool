import React from "react";
import { Box, Typography } from "@material-ui/core";
import { Skeleton } from "@material-ui/lab";
import moment from "moment";


export function PlayerVipSummary({ player, vipExpiration }) {

  if (!player) {
    return (
      <>
        <Skeleton animation="wave" />
        <Skeleton animation="wave" />
        <Skeleton animation="wave" />
      </>
    )
  }

  return (
    <Box style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
      <Typography>Name: <span style={{ fontWeight: 500 }}>{getPlayerNames(player)}</span></Typography>
      <Typography>Player ID: <span style={{ fontWeight: 500 }}>{player.get("player_id")}</span></Typography>
      <Typography>VIP Expires: <span style={{ fontWeight: 500 }}>{getExpirationDate(vipExpiration)}</span></Typography>
    </Box>
  );
}

function getExpirationDate(vipExpiration) {
  return vipExpiration ? `${moment(vipExpiration).format("lll")} (${moment(vipExpiration).fromNow()})` : "/"
}

function getPlayerNames(player) {
  let output = "No name recorded yet";

  if (player?.get("names")) {
    /* get_history_players.result.names[{
      created: string
      id: number
      last_seen: string
      name: string
      player_id: string
    }]
    */
    output = player.get("names").map(details => details.get("name")).join(", ")
  }

  if (player?.get("name")) {
    /* get_players.result[{
      country: null | string
      is_vip: boolean
      name: string
      player_id: string
      profile: PlayerProfile
      steam_bans: null | []
    }]
    */
    output = player.get("name")
  }

  return output;
}