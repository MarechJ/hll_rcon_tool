import { Grid, Link } from "@mui/material";
import React from "react";
import { List } from "immutable";
import Tooltip from "@mui/material/Tooltip";
import { getEmojiFlag } from "../../../utils/emoji";
import "emoji-mart/css/emoji-mart.css";

export const PlayerFlags = ({ player, onDeleteFlag }) => {
  return (
    (<Grid container alignItems="center" justifyContent="center">
      <Grid item style={{ height: "22px" }}></Grid>
      {player.get("flags", new List()).map((d) => (
        <Grid
          item
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
