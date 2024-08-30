import { Grid, GridList, GridListTile } from "@material-ui/core";
import React from "react";
import "emoji-mart/css/emoji-mart.css";
import { ActionButton } from "./PlayerTile/ActionButton";
import { PlayerHeader } from "./PlayerTile/PlayerHeader";
import { PlayerFlags } from "./PlayerTile/PlayerFlags";
import { PlayerSighthings } from "./PlayerTile/PlayerSighthings";
import { PlayerPenalties } from "./PlayerTile/PlayerPenalties";
import { PlayerBan } from "./PlayerTile/PlayerBan";
import withWidth from "@material-ui/core/withWidth";
import { pure } from "recompose";

const PlayerGrid = withWidth()(
  ({
    players,
    onBlacklist,
    onUnBlacklist,
    onUnban,
    onflag,
    onDeleteFlag,
    onAddVip,
    onDeleteVip,
    onTempBan,
    onPermaBan,
    onAddToWatchList,
    onRemoveFromWatchList,
    width,
    vips,
    bans,
  }) => {

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
                  key={player.get("player_id")}
                  style={{ minHeight: "100%" }}
                >
                  <Grid
                    container
                    direction="column"
                    justify="space-between"
                  >
                    <PlayerHeader player={player} />
                    <React.Fragment>
                      <PlayerFlags
                        player={player}
                        onDeleteFlag={onDeleteFlag}
                      />
                      <PlayerBan
                        bans={bans}
                        player={player}
                      />
                      <PlayerSighthings player={player} />
                      <PlayerPenalties player={player} />
                      <Grid container justify="center">
                        <Grid item>
                          <ActionButton
                            blacklisted={player.get("is_blacklisted")}
                            onUnBlacklist={() => onUnBlacklist(player)}
                            onBlacklist={() => onBlacklist(player)}
                            onTempBan={() => onTempBan(player)}
                            onPermaBan={() => onPermaBan(player)}
                            onUnban={() => onUnban(player)}
                            onflag={() => onflag(player)}
                            isVip={vips.get(player.get("player_id"))}
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

export default pure(PlayerGrid);
