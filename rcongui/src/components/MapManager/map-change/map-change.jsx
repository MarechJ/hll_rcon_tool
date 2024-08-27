import {
  Box,
  Button,
  createStyles,
  makeStyles,
  Typography,
} from "@material-ui/core";
import { Alert } from "@material-ui/lab";
import React from "react";
import { get, getServerStatus } from "../../../utils/fetchUtils";
import { MapList } from "../map-list";

const useStyles = makeStyles((theme) =>
  createStyles({
    panel: {
      display: "flex",
      flexDirection: "row",
      gap: theme.spacing(1),
      alignItems: "center",
      paddingTop: theme.spacing(1),
      paddingBottom: theme.spacing(1),
    },
  })
);

const UPDATE_INTERVAL = 60 * 1000;

function MapChange() {
  const [currentMap, setCurrentMap] = React.useState(null);
  const [maps, setMaps] = React.useState([]);
  const statusIntervalRef = React.useRef(null);
  const classes = useStyles();

  const updateServerStatus = async () => {
    const status = await getServerStatus();
    if (status) {
      setCurrentMap(status.map);
    }
  };

  const getMaps = async () => {
    const response = await get("get_maps");
    const data = await response.json();
    if (data.result) {
      setMaps(data.result);
    }
  };

  React.useEffect(() => {
    updateServerStatus();
    getMaps();
    statusIntervalRef.current = setInterval(
      updateServerStatus,
      UPDATE_INTERVAL
    );
    return () => clearInterval(statusIntervalRef.current);
  }, []);

  return (
    <>
      <Alert severity="info">
        Any change will replace the current map in 60 seconds.
      </Alert>
      <Box className={classes.panel}>
        <Typography variant="subtitle1" component={"span"}>Current map: {currentMap?.pretty_name ?? "Loading..."}</Typography>
        <Button variant="outlined" size="small">
          Switch Allies
        </Button>
        <Button variant="outlined" size="small">
          Switch Axis
        </Button>
        <Button variant="outlined" size="small">
          Reset
        </Button>
      </Box>
      <MapList mapLayers={maps} />
    </>
  );
}

export default MapChange;
