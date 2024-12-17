import { ImageList, ImageListItem } from "@mui/material";
import { ActionButton } from "./PlayerTile/ActionButton";
import { PlayerHeader } from "./PlayerTile/PlayerHeader";
import { PlayerFlags } from "./PlayerTile/PlayerFlags";
import { PlayerSighthings } from "./PlayerTile/PlayerSighthings";
import { PlayerPenalties } from "./PlayerTile/PlayerPenalties";
import { PlayerBan } from "./PlayerTile/PlayerBan";
import Grid from "@mui/material/Grid2";
import {Fragment} from "react";

const PlayerGrid = ({
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
  vips,
  bans,
}) => {
  const size = {
    xs: 1,
    sm: 2,
    md: 3,
    lg: 4,
    xl: 5,
  }[2];

  return (
    (<Grid container>
      <Grid size={12}>
        <ImageList cols={size} cellHeight={240} spacing={12}>
          {players.map((player) => {
            return (
              <ImageListItem
                key={player.get("player_id")}
                style={{ minHeight: "100%" }}
              >
                <Grid
                  container
                  direction="column"
                  justifyContent="space-between"
                >
                  <PlayerHeader player={player} />
                  <Fragment>
                    <PlayerFlags player={player} onDeleteFlag={onDeleteFlag} />
                    <PlayerBan bans={bans} player={player} />
                    <PlayerSighthings player={player} />
                    <PlayerPenalties player={player} />
                    <Grid container justifyContent="center">
                      <Grid>
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
                  </Fragment>
                </Grid>
              </ImageListItem>
            );
          })}
        </ImageList>
      </Grid>
    </Grid>)
  );
};

export default PlayerGrid;
