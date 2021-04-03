import { Grid, GridListTile, makeStyles } from "@material-ui/core";
import React from "react";
import { ActionButton } from "./ActionButton";
import { PlayerHeader } from "./PlayerHeader";
import { PlayerFlags } from "./PlayerFlags";
import { PlayerSighthings } from "./PlayerSighthings";
import { PlayerPenalties } from "./PlayerPenalties";

const useStyles = makeStyles((theme) => ({
  paperTile: {
    backgroundColor: theme.palette.background.paper,
    minHeight: "100%",
    padding: theme.spacing(2),
  },
  root: {
    display: "flex",
    flexWrap: "wrap",
    justifyContent: "space-around",
    overflow: "hidden",
  },
}));

export default ({ classes, onDeleteFlag, player }) => {
  const myClasses = useStyles();

  return (
    <GridListTile style={{ minHeight: "100%" }}>
      <Grid
        container
        className={myClasses.paperTile}
        direction="column"
        justify="space-between"
      >
        <PlayerHeader classes={classes} player={player} />
        <PlayerFlags
          player={player}
          classes={classes}
          onDeleteFlag={onDeleteFlag}
        />
        <PlayerSighthings classes={classes} player={player} />
        <PlayerPenalties classes={classes} player={player} />
        <Grid container justify="center">
          <Grid item>
            <ActionButton
              blacklisted={false}
              onUnBlacklist={() => null}
              onBlacklist={() => null}
              onTempBan={() => null}
              onUnban={() => null}
              onflag={() => null}
              isVip={false}
              onAddVip={() => null}
              onDeleteVip={() => null}
              isWatched={false}
              onAddToWatchList={() => null}
              onRemoveFromWatchList={() => null}
            />
          </Grid>
        </Grid>
      </Grid>
    </GridListTile>
  );
};
