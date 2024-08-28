import {
  Box,
  Button,
  createStyles,
  FormControl,
  FormControlLabel,
  FormLabel,
  makeStyles,
  Paper,
  Radio,
  RadioGroup,
  Typography,
} from "@material-ui/core";
import React from "react";
import { getServerStatus } from "../../../utils/fetchUtils";
import { generateInitialState, getTacMapImageSrc } from "../helpers";
import { Skeleton } from "@material-ui/lab";
import clsx from "clsx";

const UPDATE_INTERVAL = 5 * 1000;

const UP = [-1, 0];
const DOWN = [1, 0];
const LEFT = [0, -1];
const RIGHT = [0, 1];

const flip = (o) =>
  o.map((row, x) => {
    const arr = Array(row.lenght);
    o.forEach((r, y) => {
      arr[y] = r[x];
    });
    return arr;
  });

const reduceToInts = (arr) =>
  arr.reduce((acc, row) => {
    const i = row.indexOf(true);
    return acc.concat(i === -1 ? null : i - 1);
  }, []);

const useStyles = makeStyles((theme) =>
  createStyles({
    main: {
      display: "flex",
      flexDirection: "column",
      gap: theme.spacing(1),
    },
    panel: {
      display: "flex",
      flexDirection: "row",
      gap: theme.spacing(1),
      alignItems: "center",
    },
    map: {
      position: "absolute",
      top: 0,
      left: 0,
      width: "100%",
      height: "100%",
    },
    mapImg: {
      width: "100%",
      height: "100%",
      touchAction: "none",
    },
    grid: {
      position: "relative",
      display: "grid",
      gridTemplateColumns: "repeat(5, 1fr)",
      gridTemplateRows: "repeat(5, 1fr)",
      width: "100%",
      height: "100%",
    },
    controlGrid: {
      position: "relative",
      display: "grid",
      gridTemplateColumns: "repeat(5, 1fr)",
      gridTemplateRows: "repeat(5, 1fr)",
      gap: theme.spacing(0.5),
      width: "100%",
      height: "100%",
    },
    gridContainer: {
      position: "relative",
      maxWidth: 650,
      minWidth: 280,
      aspectRatio: "1 / 1",
    },
    controlContainer: {
      width: "fit-content",
    },
    controlBtn: {
      border: "4px ridge black",
      minWidth: 0,
      padding: 0,
      borderRadius: 0,
      opacity: 0.35,
      "&:hover": {
        borderStyle: "inset",
      },
    },
    controlBtnSelected: {
      background: theme.palette.success.main,
      borderStyle: "inset",
      "&:hover": {
        background: theme.palette.success.dark,
      },
    },
    selected: {
      opacity: 0.25,
      background: theme.palette.success.main,
      border: "2px solid",
      borderColor: "2px solid white",
    },
    unavailable: {
      backgroundImage:
        "repeating-linear-gradient(45deg, #ff7700 0, #ff7700 2px, transparent 0, transparent 50%);",
      backgroundSize: "10px 10px",
    },
    disabled: {
      backgroundImage:
        "repeating-linear-gradient(45deg, #000 0, #000 2px, transparent 0, transparent 50%);",
      backgroundSize: "20px 20px",
    },
  })
);

function MapObjectives() {
  const [currentMap, setCurrentMap] = React.useState(null);
  const [randomConstraint, setRandomConstraint] = React.useState("0");
  const [objectives, setObjectives] = React.useState(
    generateInitialState("horizontal", false)
  );
  const statusIntervalRef = React.useRef(null);
  const classes = useStyles();

  const updateServerStatus = async () => {
    const status = await getServerStatus();
    if (status) {
      (status.map.orientation = "horizontal"), setCurrentMap(status.map);
    }
  };

  const isButtonUnavailable = (state) => {
    return state === null;
  };

  const isButtonDisabled = (state, index) => {
    const size = 5;
    const targetIndex = index % size;
    const targetRow = Math.floor(index / size);

    // Helper function to check if adjacent cells in a specific direction are selected
    const isAdjacentSelected = (dx, dy, rowIndex, colIndex) => {
      const newRow = rowIndex + dx;
      const newCol = colIndex + dy;

      if (newRow >= 0 && newRow < size && newCol >= 0 && newCol < size) {
        if (currentMap.orientation === "vertical") {
          const adjacentSelected = objectives[newRow].indexOf(true);
          return (
            adjacentSelected >= 0 &&
            Math.abs(adjacentSelected - targetIndex) > 1
          );
        } else {
          const adjacentSelected = objectives.findIndex(
            (row) => row[newCol] === true
          );
          return (
            adjacentSelected >= 0 && Math.abs(adjacentSelected - targetRow) > 1
          );
        }
      }
      return false;
    };

    // Is unavailable
    if (isButtonUnavailable(state)) {
      return true;
    }

    // Is selected
    if (state === true) return false;

    // Check for vertical orientation
    if (currentMap.orientation === "vertical") {
      // but there is another selected in the row
      if (objectives[targetRow].includes(true)) return true;

      // Check adjacent cells vertically (UP, DOWN)
      if (
        isAdjacentSelected(UP[0], UP[1], targetRow, targetIndex) ||
        isAdjacentSelected(DOWN[0], DOWN[1], targetRow, targetIndex)
      ) {
        return true;
      }
    } else {
      // Check for horizontal orientation
      // but there is another selected in the column
      if (objectives.some((row) => row[targetIndex] === true)) return true;

      // Check adjacent cells horizontally (LEFT, RIGHT)
      if (
        isAdjacentSelected(LEFT[0], LEFT[1], targetRow, targetIndex) ||
        isAdjacentSelected(RIGHT[0], RIGHT[1], targetRow, targetIndex)
      ) {
        return true;
      }
    }

    return false;
  };

  const handleSelectClick = (index) => {
    const targetIndex = index % 5;
    const targetRow = Math.floor(index / 5);
    setObjectives((prevObjectives) =>
      prevObjectives.map((row, rowIndex) =>
        row.map((item, itemIndex) =>
          rowIndex === targetRow && itemIndex === targetIndex ? !item : item
        )
      )
    );
  };

  const handleChangeLayoutClick = () => {
    const payload = reduceToInts(
      objectives[1][0] !== null ? flip(objectives) : objectives
    );
    console.log(payload);
  };

  const handleConstraintChange = (event) => {
    setRandomConstraint(event.target.value);
  };

  React.useEffect(() => {
    updateServerStatus();
    statusIntervalRef.current = setInterval(
      updateServerStatus,
      UPDATE_INTERVAL
    );
    return () => clearInterval(statusIntervalRef.current);
  }, []);

  return (
    <Box className={classes.main}>
      <Box className={classes.panel}>
        <Button
          color="secondary"
          variant="outlined"
          size="small"
          onClick={handleChangeLayoutClick}
        >
          CHANGE LAYOUT
        </Button>
      </Box>
      {currentMap ? (
        <Box className={classes.gridContainer}>
          <Box className={classes.map}>
            <img
              className={classes.mapImg}
              src={getTacMapImageSrc(currentMap)}
              alt=""
              draggable={false}
            />
          </Box>
          <Box className={classes.grid}>
            {objectives.flat().map((state, index) => {
              return (
                <Button
                  key={index}
                  onClick={() => handleSelectClick(index)}
                  disabled={isButtonDisabled(state, index)}
                  className={clsx(
                    classes.controlBtn,
                    isButtonUnavailable(state) && classes.unavailable,
                    state === true && classes.controlBtnSelected,
                    state === false &&
                      isButtonDisabled(state, index) &&
                      classes.disabled
                  )}
                ></Button>
              );
            })}
          </Box>
        </Box>
      ) : (
        <Skeleton width="100%" height={"100%"} />
      )}
      <Box className={classes.controlContainer}>
        <Typography>
          When you omit any objective selection, the objectives will be chosen
          by the following constraints.
        </Typography>
        <FormControl component="fieldset">
          <FormLabel component="legend">Random contraints</FormLabel>
          <RadioGroup
            aria-label="Random contraints"
            name="random-constraints"
            value={randomConstraint}
            onChange={handleConstraintChange}
          >
            <FormControlLabel
              value={"0"}
              control={<Radio />}
              label={"No constraints"}
            />
            <FormControlLabel
              value={"1"}
              control={<Radio />}
              label="Points must be adjacent"
            />
            <FormControlLabel
              value={"2"}
              control={<Radio />}
              label="No straight line"
            />
            <FormControlLabel
              value={"3"}
              control={<Radio />}
              label="Adjacent and No line combined"
            />
          </RadioGroup>
        </FormControl>
      </Box>
    </Box>
  );
}

export default MapObjectives;
