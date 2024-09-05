import { createStyles, makeStyles, Typography } from "@material-ui/core";
import MapRotationSettings from "./map-rotation-config";
import MapRotation from "./map-rotation";

const useStyles = makeStyles((theme) =>
  createStyles({
    text: {
      marginTop: theme.spacing(2),
      marginBottom: theme.spacing(2),
      borderBottom: "1px solid",
      borderColor: theme.palette.divider,
    },
  })
);

function MapRotationConfig() {
  const classes = useStyles();

  return (
    <>
      <MapRotation />
      <Typography className={classes.text} variant="h6">
        Other settings
      </Typography>
      <MapRotationSettings />
    </>
  );
}

export default MapRotationConfig;
