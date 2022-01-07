import { Grid } from "@material-ui/core";
import React from "react";
import Tooltip from "@material-ui/core/Tooltip";
import moment from "moment";

export const PlayerSighthings = ({ classes, player }) => {
  const first_seen = moment(player.get("first_seen_timestamp_ms"));
  const last_seen = moment(player.get("last_seen_timestamp_ms"));
  const now = moment();

  return (
    <Grid
      container
      justify="space-between"
      spacing={0}
      className={classes.noPaddingMargin}
    >
      <Grid item xs={6}>
        <Tooltip title={first_seen.format("LLLL")} arrow>
          <small>
            First seen {moment.duration(now.diff(first_seen)).humanize()} ago
          </small>
        </Tooltip>
      </Grid>
      <Grid item xs={6}>
        <Tooltip title={last_seen.format("LLLL")} arrow>
          <small>
            Last seen {moment.duration(now.diff(last_seen)).humanize()} ago
          </small>
        </Tooltip>
      </Grid>
    </Grid>
  );
};
