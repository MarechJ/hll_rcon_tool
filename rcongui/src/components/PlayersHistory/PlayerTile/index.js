import { Grid, GridListTile } from "@material-ui/core";
import React from "react";
import { ActionButton } from "./ActionButton";
import { PlayerHeader } from "./PlayerHeader";
import { PlayerFlags } from "./PlayerFlags";
import { PlayerSighthings } from "./PlayerSighthings";
import { PlayerPenalties } from "./PlayerPenalties";

export default ({ onDeleteFlag, player }) => {

  return (
    <GridListTile style={{ minHeight: "100%" }}>
      <Grid
        container
        direction="column"
        justify="space-between"
      >
        <PlayerHeader player={player} />
        <PlayerFlags
          player={player}
          onDeleteFlag={onDeleteFlag}
        />
        <PlayerSighthings player={player} />
        <PlayerPenalties player={player} />
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
