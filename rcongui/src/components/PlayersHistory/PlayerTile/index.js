import { ImageListItem } from "@mui/material";
import React from "react";
import { ActionButton } from "./ActionButton";
import { PlayerHeader } from "./PlayerHeader";
import { PlayerFlags } from "./PlayerFlags";
import { PlayerSighthings } from "./PlayerSighthings";
import { PlayerPenalties } from "./PlayerPenalties";
import Grid from "@mui/material/Grid2";

export default ({ onDeleteFlag, player }) => {

  return (
    (<ImageListItem style={{ minHeight: "100%" }}>
      <Grid
        container
        direction="column"
        justifyContent="space-between"
      >
        <PlayerHeader player={player} />
        <PlayerFlags
          player={player}
          onDeleteFlag={onDeleteFlag}
        />
        <PlayerSighthings player={player} />
        <PlayerPenalties player={player} />
        <Grid container justifyContent="center">
          <Grid>
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
    </ImageListItem>)
  );
};
