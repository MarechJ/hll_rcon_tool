import { Grid, GridList, GridListTile, makeStyles } from "@material-ui/core";
import React from "react";
// import "emoji-mart/css/emoji-mart.css";
import { ActionButton } from "./PlayerTile/ActionButton";
import { PlayerHeader } from "./PlayerTile/PlayerHeader";
import { PlayerFlags } from "./PlayerTile/PlayerFlags";
import { PlayerSighthings } from "./PlayerTile/PlayerSighthings";
import { PlayerPenalties } from "./PlayerTile/PlayerPenalties";
import { PlayerBan } from "./PlayerTile/PlayerBan";
import withWidth from "@material-ui/core/withWidth";

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

const PlayerGrid = withWidth()(
  ({
    classes,
    players,
    onBlacklist,
    onUnBlacklist,
    onUnban,
    onflag,
    onDeleteFlag,
    onAddVip,
    onDeleteVip,
    onTempBan,
    onAddToWatchList,
    onRemoveFromWatchList,
    width,
    vips,
    bans
  }) => {
    const myClasses = useStyles();

    const size = {
      xs: 1,
      sm: 2,
      md: 3,
      lg: 4,
      xl: 5,
    }[width];

    return (
      <Grid container>
        <Grid item xs={12}>
          <GridList cols={size} cellHeight={240} spacing={12}>
            {players.map((player) => {
              return (
                <GridListTile
                  key={player.get("steam_id_64")}
                  style={{ minHeight: "100%" }}
                >
                  <Grid
                    container
                    className={myClasses.paperTile}
                    direction="column"
                    justify="space-between"
                  >
                    <PlayerHeader classes={classes} player={player} />
                    <React.Fragment>
                      <PlayerFlags
                        player={player}
                        classes={classes}
                        onDeleteFlag={onDeleteFlag}
                      />
                      <PlayerBan classes={classes} bans={bans} player={player} />
                      <PlayerSighthings classes={classes} player={player} />
                      <PlayerPenalties classes={classes} player={player} />
                      <Grid container justify="center">
                        <Grid item>
                          <ActionButton
                            blacklisted={
                              player.get("blacklist") &&
                              player.get("blacklist").get("is_blacklisted")
                            }
                            onUnBlacklist={() => onUnBlacklist(player)}
                            onBlacklist={() => onBlacklist(player)}
                            onTempBan={() => onTempBan(player)}
                            onUnban={() => onUnban(player)}
                            onflag={() => onflag(player)}
                            isVip={vips.get(player.get("steam_id_64"))}
                            onAddVip={() => onAddVip(player)}
                            onDeleteVip={() => onDeleteVip(player)}
                            isWatched={
                              player.get("watchlist") &&
                              player.get("watchlist").get("is_watched")
                            }
                            onAddToWatchList={() => onAddToWatchList(player)}
                            onRemoveFromWatchList={() =>
                              onRemoveFromWatchList(player)
                            }
                          />
                        </Grid>
                      </Grid>
                    </React.Fragment>
                  </Grid>
                </GridListTile>
              );
            })}
          </GridList>
        </Grid>
      </Grid>
    );
  }
);

export default PlayerGrid;
