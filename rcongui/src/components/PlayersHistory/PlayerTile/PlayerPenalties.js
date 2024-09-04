import Grid from "@mui/material/Unstable_Grid2";
import React from "react";
import { WithPopver } from "../../commonComponent";
import moment from "moment";
import { List } from "immutable";

function truncateString(str, num) {
  // If the length of str is less than or equal to num
  // just return str--don't truncate it.
  if (str.length <= num) {
    return str;
  }
  // Return str truncated with '...' concatenated to the end of str.
  return str.slice(0, num) + "...";
}

export const Penalites = ({ player }) => (
  <div>
    {player.get("received_actions", new List()).size < 1 ? "Clean record" : ""}
    {player.get("received_actions", new List()).map((action) => (
      <p>{`${action.get("action_type")} ${moment.utc(action.get("time")).local().format(
        "ddd Do MMM HH:mm:ss"
      )}: ${truncateString(action.get("reason"), 50)} by ${action.get(
        "by"
      )}`}</p>
    ))}
  </div>
);

export const PlayerPenalties = ({ player }) => (
  <Grid container>
    <Grid xs={12}>
      <WithPopver
        popoverContent={<Penalites player={player} />}
      >
        <small>
          {player
            .get("penalty_count")
            .map((v, k) => `${k}: ${v}`)
            .join(" ")}
        </small>
      </WithPopver>
    </Grid>
  </Grid>
);
