import { Grid, Link } from "@material-ui/core";
import React from "react";
import { List } from "immutable";
import Tooltip from "@material-ui/core/Tooltip";
import { getEmojiFlag } from "../../../utils/emoji";
// import "emoji-mart/css/emoji-mart.css";

export const PlayerFlags = ({ player, classes, onDeleteFlag }) => {
  return (
    <Grid container alignItems="center" justify="center">
      <Grid item style={{ height: "22px" }}></Grid>
      {player.get("flags", new List()).map((d) => (
        <Grid
          item
          className={classes.noPaddingMargin}
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
    </Grid>
  );
};
