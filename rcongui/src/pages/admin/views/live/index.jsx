import React from "react";
import Grid from "@mui/material/Grid2";
import PlayerView from "@/components/PlayerView";
import Logs from "@/components/LogsView/logs";
import GameLogs from "@/components/LiveLogs"

const Live = () => {
  const [mdSize, setMdSize] = React.useState(6);
  const [direction, setDirection] = React.useState("");
  const isFullScreen = () => mdSize !== 6;
  const toggleMdSize = () => (isFullScreen() ? setMdSize(6) : setMdSize(12));

  return (
    (<Grid container spacing={1}>
      <Grid
        size={{
          sm: 12,
          md: mdSize
        }}>
        <PlayerView
          onFullScreen={() => {
            setDirection("");
            toggleMdSize();
          }}
          isFullScreen={isFullScreen()}
        />
      </Grid>
      <Grid
        size={{
          sm: 12,
          md: mdSize
        }}>
        <GameLogs />
      </Grid>
    </Grid>)
  );
};

export default Live;
