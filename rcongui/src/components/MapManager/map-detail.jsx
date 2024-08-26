import {
  Box,
  createStyles,
  Divider,
  makeStyles,
  Typography,
} from "@material-ui/core";
import { unifiedGamemodeName } from "./helpers";

const useStyles = makeStyles((theme) =>
  createStyles({
    root: {
      display: "flex",
      flexWrap: "wrap",
      gap: theme.spacing(0.5),
      textTransform: "capitalize",
    },
  })
);

export function MapDetail({ mapLayer }) {
  const classes = useStyles();

  const gameMode = unifiedGamemodeName(mapLayer.game_mode)

  return (
    <Box className={classes.root}>
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
