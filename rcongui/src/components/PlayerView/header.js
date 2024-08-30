import React from "react";
import Grid from "@material-ui/core/Grid";
import ListItemText from "@material-ui/core/ListItemText";
import LinearProgress from "@material-ui/core/LinearProgress";
import "react-toastify/dist/ReactToastify.css";
import Button from "@material-ui/core/Button";
import Link from "@material-ui/core/Link";
import { toast } from "react-toastify";
import ButtonGroup from "@material-ui/core/ButtonGroup";
import FullscreenIcon from "@material-ui/icons/Fullscreen";
import FullscreenExitIcon from "@material-ui/icons/FullscreenExit";
import { IconButton } from "@material-ui/core";

const AutoRefreshBar = ({
  intervalFunction,
  everyMs,
  refreshIntevalMs,
  onGroupActionClick,
  onUnbanClick,
  onFullScreenClick,
  isFullScreen,
}) => {
  const [completed, setCompleted] = React.useState(0);

  React.useEffect(() => {
    function progress() {
      setCompleted((oldCompleted) => {
        if (oldCompleted === 100) {
          intervalFunction();
          return 0;
        }

        return Math.min(oldCompleted + (refreshIntevalMs / everyMs) * 100, 100);
      });
    }

    const timer = setInterval(progress, refreshIntevalMs);
    return () => {
      clearInterval(timer);
    };
  }, [everyMs, intervalFunction, refreshIntevalMs]);

  return (
    <React.Fragment>
      <Grid  container justify="flex-start">
        <Grid item xs={12}>
          <Grid container justify="space-between">
            <Grid style={{ textAlign: "left" }} item xs={6}>
              <h1>
                Players view{" "}
                <IconButton onClick={onFullScreenClick}>
                  {isFullScreen ? <FullscreenExitIcon /> : <FullscreenIcon />}
                </IconButton>
              </h1>
            </Grid>
            <Grid item xs={6} style={{ textAlign: "right" }}>
              <ButtonGroup
                
                orientation="vertical"
                color="primary"
                variant="contained"
                aria-label="vertical outlined primary button group"
              >
                <Button onClick={onGroupActionClick}>Group action</Button>
                <Button onClick={onUnbanClick}>Unban</Button>
              </ButtonGroup>
            </Grid>
          </Grid>
        </Grid>
        <Grid item xs={12}>
          <Link
            style={{ cursor: "pointer" }}
            onClick={() =>
              intervalFunction().then(() => toast.success("Refreshed"))
            }
          >
            <ListItemText secondary="Refresh now. Next auto refresh:" />
          </Link>
        </Grid>
      </Grid>
      <LinearProgress
        variant="determinate"
        value={completed}
        
      />
    </React.Fragment>
  );
};

export default AutoRefreshBar;
