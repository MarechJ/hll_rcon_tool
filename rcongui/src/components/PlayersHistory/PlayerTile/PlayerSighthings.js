import Grid from "@mui/material/Grid2";
import React from "react";
import Tooltip from "@mui/material/Tooltip";
import moment from "moment";

export const PlayerSighthings = ({ player }) => {
  const first_seen = moment(player.get("first_seen_timestamp_ms"));
  const last_seen = moment(player.get("last_seen_timestamp_ms"));

  let vip_expiration;
  if (player.get("vip_expiration")) {
    vip_expiration = moment(player.get("vip_expiration"));
  }

  const now = moment();
  const humanizedExpiration = moment
    .duration(now.diff(vip_expiration))
    .humanize();

  let vipDisplay;
  if (vip_expiration?.isBefore(moment.now())) {
    vipDisplay = (
      <small style={{ color: "red" }}>
        VIP expired {humanizedExpiration} ago
      </small>
    );
  } else if (vip_expiration?.isSameOrAfter(moment().add(100, "years"))) {
    vipDisplay = <small>VIP Never Expires</small>;
  } else if (vip_expiration) {
    vipDisplay = <small>VIP expires in {humanizedExpiration}</small>;
  }

  return (
    (<Grid
        container
        justifyContent="space-between"
        spacing={0}
      >
      {vip_expiration ? (
        <Grid size={12}>
          <Tooltip title={vip_expiration.format("LLLL")} arrow>
            {vipDisplay}
          </Tooltip>
        </Grid>
      ) : (
        ""
      )}
      <Grid size={6}>
        <Tooltip title={first_seen.format("LLLL")} arrow>
          <small>
            First seen {moment.duration(now.diff(first_seen)).humanize()} ago
          </small>
        </Tooltip>
      </Grid>
      <Grid size={6}>
        <Tooltip title={last_seen.format("LLLL")} arrow>
          <small>
            Last seen {moment.duration(now.diff(last_seen)).humanize()} ago
          </small>
        </Tooltip>
      </Grid>
    </Grid>)
  );
};
