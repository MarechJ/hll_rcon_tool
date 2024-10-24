import { Avatar, Box, Divider, Typography } from "@mui/material";
import { makeStyles } from '@mui/styles';
import { getMapLayerImageSrc, unifiedGamemodeName } from "./helpers";

const useStyles = makeStyles((theme) => ({
  descriptionRoot: {
    display: "flex",
    flexWrap: "wrap",
    gap: theme.spacing(0.5),
    textTransform: "capitalize",
  },
  mapBox: {
    display: "flex",
    gap: theme.spacing(1),
    alignItems: "center",
  },
  mapBoxAvatar: {
    display: "none",
    [theme.breakpoints.up("sm")]: {
      display: "block",
    },
  },
}));

export function MapDescription({ mapLayer }) {
  const classes = useStyles();

  const gameMode = unifiedGamemodeName(mapLayer.game_mode);

  return (
    <Box className={classes.descriptionRoot}>
      <Typography variant="caption">{gameMode}</Typography>
      {gameMode === "offensive" && (
        <>
          <Divider orientation="vertical" flexItem />
          <Typography variant="caption">{mapLayer.attackers}</Typography>
        </>
      )}
      <Divider orientation="vertical" flexItem />
      <Typography variant="caption">{mapLayer.environment}</Typography>
    </Box>
  );
}

export function MapAvatar({ mapLayer, ...props }) {
  return <Avatar src={getMapLayerImageSrc(mapLayer)} {...props} />;
}

export function MapDetail({ mapLayer }) {
  const classes = useStyles();

  return (
    <Box className={classes.mapBox}>
      <MapAvatar mapLayer={mapLayer} className={classes.mapBoxAvatar} />
      <Box>
        <Typography variant="subtitle1">{mapLayer.map.pretty_name}</Typography>
        <MapDescription mapLayer={mapLayer} />
      </Box>
    </Box>
  );
}
