import React from "react"
import LinearProgress from "@material-ui/core/LinearProgress"

const AutoRefreshLine = ({
    intervalFunction,
    classes,
    execEveryMs,
    statusRefreshIntervalMs = 1000,
  }) => {
    const [completed, setCompleted] = React.useState(0);
  
    React.useEffect(() => {
      function progress() {
        setCompleted(oldCompleted => {
          if (oldCompleted === 100) {
            intervalFunction();
            return 0;
          }
  
          return Math.min(oldCompleted + (statusRefreshIntervalMs / execEveryMs) * 100, 100);
        });
      }
  
      const timer = setInterval(progress, statusRefreshIntervalMs);
      return () => {
        clearInterval(timer);
      };
    }, [execEveryMs, intervalFunction, statusRefreshIntervalMs]);
  
    return (
      <React.Fragment>
        <LinearProgress
          variant="determinate"
          value={completed}
          className={classes.marginBottom}
        />
      </React.Fragment>
    );
  };

export default AutoRefreshLine