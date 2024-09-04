import { Avatar, Box, Divider, Typography } from "@mui/material";
import makeStyles from '@mui/styles/makeStyles';
import { getMapLayerImageSrc, unifiedGamemodeName } from "./helpers";
import { styled } from "@mui/material/styles"

const Wrapper = styled('div')(({ theme }) => ({
  display: "flex",
  flexWrap: "wrap",
  gap: theme.spacing(0.5),
  textTransform: "capitalize",
}));

export function MapDetails({ mapLayer }) {
  const gameMode = unifiedGamemodeName(mapLayer.game_mode)

  return (
    <Wrapper>
      <Typography variant="caption">{gameMode}</Typography>
      {gameMode === "offensive" && (
        <>
          <Divider orientation="vertical" flexItem />
          <Typography variant="caption">{mapLayer.attackers}</Typography>
        </>
      )}
      <Divider orientation="vertical" flexItem />
      <Typography variant="caption">{mapLayer.environment}</Typography>
    </Wrapper>
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
