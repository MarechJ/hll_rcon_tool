import { Link } from "@mui/material";
import React from "react";
import { List } from "immutable";
import Tooltip from "@mui/material/Tooltip";
import { getEmojiFlag } from "../../../utils/emoji";
import Grid from "@mui/material/Grid2";

export const PlayerFlags = ({ player, onDeleteFlag }) => {
  return (
    (<Grid container alignItems="center" justifyContent="center">
      <Grid style={{ height: "22px" }}></Grid>
      {player.get("flags", new List()).map((d) => (
        <Grid
          
          style={{ height: "22px" }}
        >
          <Tooltip
            title={d.get("comment") ? d.get("comment") : "<empty>"}
            arrow
          >
            <Link
              onClick={() =>
                window.confirm("Delete flag?") ? onDeleteFlag(d.get("id")) : ""
              }
            >
              {getEmojiFlag(d.get("flag"))}
            </Link>
          </Tooltip>
        </Grid>
      ))}
    </Grid>)
  );
};
