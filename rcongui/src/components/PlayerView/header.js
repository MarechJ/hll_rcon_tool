import React, { Component } from "react";
import Grid from "@material-ui/core/Grid";
import ListItemText from "@material-ui/core/ListItemText";
import _ from "lodash";
import LinearProgress from "@material-ui/core/LinearProgress";
import "react-toastify/dist/ReactToastify.css";
import useStyles from "../useStyles";
import Button from "@material-ui/core/Button";
import Link from "@material-ui/core/Link";
import { toast } from "react-toastify";

const AutoRefreshBar = ({
  intervalFunction,
  everyMs,
  refreshIntevalMs,
  onGroupActionClick
}) => {
  const classes = useStyles();
  const [completed, setCompleted] = React.useState(0);

  React.useEffect(() => {
    function progress() {
      setCompleted(oldCompleted => {
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
      <Grid className={classes.textLeft} container justify="flex-start">
        <Grid item xs={12}>
          <Grid container justify="space-between">
            <Grid style={{ textAlign: "left"}} item xs={6}>
              <h1>Players view</h1>
            </Grid>
            <Grid item xs={6} style={{ textAlign: "right"}}>
              <h1>
                <Button
                  variant="contained"
                  color="primary"
                  disableElevation
                  onClick={onGroupActionClick}
                >
                  Group action
                </Button>
              </h1>
            </Grid>
          </Grid>
        </Grid>
        <Grid item xs={12}>
          <Link style={{cursor: 'pointer'}} onClick={() => intervalFunction().then(() => toast.success("Refreshed"))}>
            <ListItemText secondary="Refresh now. Next auto refresh:" />
          </Link>
        </Grid>
      </Grid>
      <LinearProgress
        variant="determinate"
        value={completed}
        className={classes.marginBottom}
      />
    </React.Fragment>
  );
};

export default AutoRefreshBar;
