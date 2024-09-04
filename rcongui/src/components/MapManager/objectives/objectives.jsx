import {
  Box,
  Button,
  Checkbox,
  CircularProgress,
  FormControl,
  FormControlLabel,
  FormGroup,
  FormLabel,
} from "@mui/material";
import createStyles from '@mui/styles/createStyles';
import makeStyles from '@mui/styles/makeStyles';
import React from "react";
import { changeGameLayout, getMapObjectives, getServerStatus } from "../../../utils/fetchUtils";
import {
  generateObjectivesGrid,
  getTacMapImageSrc,
  unifiedGamemodeName,
} from "../helpers";
import { Alert, AlertTitle, Skeleton } from '@mui/material';
import clsx from "clsx";
import { styled } from "@mui/material/styles"

const UPDATE_INTERVAL = 5 * 1000;
const CONFIRM_DELAY = 10 * 1000;

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

const Container = styled('div')(({ theme }) => ({
  display: "flex",
  flexDirection: "column",
  gap: theme.spacing(1),
}));

const ActionPanel = styled('div')(({ theme }) => ({
  display: "flex",
  flexDirection: "row",
  gap: theme.spacing(1),
  alignItems: "center",
}));

const MapWrapper = styled('div')({
  position: "absolute",
  top: 0,
  left: 0,
  width: "100%",
  height: "100%",
});

const MapImg = styled('img')({
  width: "100%",
  height: "100%",
  touchAction: "none",
});

const ObjectivesGrid = styled('div')({
  position: "relative",
  display: "grid",
  gridTemplateColumns: "repeat(5, 1fr)",
  gridTemplateRows: "repeat(5, 1fr)",
  width: "100%",
  height: "100%",
});

const ControlGrid = styled('div')(({ theme }) => ({
  position: "relative",
  display: "grid",
  gridTemplateColumns: "repeat(5, 1fr)",
  gridTemplateRows: "repeat(5, 1fr)",
  gap: theme.spacing(0.5),
  width: "100%",
  height: "100%",
}));

const ObjectivesContainer = styled('div')({
  position: "relative",
  maxWidth: 650,
  minWidth: 280,
  aspectRatio: "1 / 1",
});

const ControlContainer = styled('div')(({ theme }) => ({
  width: "fit-content",
  display: "flex",
  flexDirection: "column",
  gap: theme.spacing(2),
}));

const ControlButton = styled('button')(({ theme, state }) => ({
  border: "4px ridge black",
  minWidth: 0,
  padding: 0,
  borderRadius: 0,
  opacity: 0.35,
  "&:hover": {
    borderStyle: "inset",
  },
  ...(state === true && {
    background: theme.palette.success.main,
    borderStyle: "inset",
    "&:hover": {
      background: theme.palette.success.dark,
    },
  }),
  ...(state === false && {
    backgroundImage:
      "repeating-linear-gradient(45deg, #ff7700 0, #ff7700 2px, transparent 0, transparent 50%);",
    backgroundSize: "10px 10px",
  }),
  ...(state === null && {
    backgroundImage:
      "repeating-linear-gradient(45deg, #000 0, #000 2px, transparent 0, transparent 50%);",
    backgroundSize: "20px 20px",
  }),
}));


function MapObjectives() {
  const [currentMap, setCurrentMap] = React.useState(null);
  const [randomConstraint, setRandomConstraint] = React.useState({
    "1": false,
    "2": false,
  });
  const [objectives, setObjectives] = React.useState(null);
  const [isSaving, setIsSaving] = React.useState(false);
  const statusIntervalRef = React.useRef(null);
  const savingTimeoutRef = React.useRef(null);
  const classes = useStyles();

  const updateServerStatus = async () => {
    const status = await getServerStatus();
    if (status) {
      if (unifiedGamemodeName(status.map.game_mode) === "skirmish") {
        setObjectives(null);
      }
      if (status.map.id !== currentMap?.id) {
        setCurrentMap(status.map);
      }
    }
  };

  const isButtonUnavailable = (state) => {
    return state === null;
  };

  const isButtonDisabled = (state, index) => {
    const size = 5;
    const targetIndex = index % size;
    const targetRow = Math.floor(index / size);

    // Is unavailable
    if (isButtonUnavailable(state)) {
      return true;
    }

    // Is selected
    if (state === true) return false;

    // Is unselected
    if (currentMap.map.orientation === "vertical") {
      // but there is another selected in the row
      if (objectives[targetRow].includes(true)) return true;
    } else {
      // but there is another selected in the column
      if (objectives.some((row) => row[targetIndex] === true)) return true;
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

  const handleResetLayoutClick = () => {
    setObjectives(generateObjectivesGrid(currentMap.map.orientation))
  }

  const handleChangeLayoutClick = async () => {
    setIsSaving(true);
    const chosenObjectives = reduceToInts(
      objectives[1][0] !== null ? flip(objectives) : objectives
    );

    const constraintValue = Object.entries(randomConstraint).reduce((acc, [value, used]) => {
      if (used) return acc + Number(value);
      return acc;
    }, 0)

    const newLayout = await changeGameLayout({
      objectives: chosenObjectives,
      random_constraints: constraintValue,
    });

    const mapObjectives = await getMapObjectives();
    if (mapObjectives && newLayout) {
      // generate clear grid
      const finalObjectives = generateObjectivesGrid(currentMap.map.orientation);
      const isHorizontal = currentMap.map.orientation === "horizontal";
      // update the grid with the new objectives
      newLayout.forEach((objective, rowIndex) => {
        const row = rowIndex
        const col = mapObjectives[rowIndex].indexOf(objective)
        if (isHorizontal) {
          finalObjectives[col + 1][row] = true;
        } else {
          finalObjectives[row][col + 1] = true;
        }
      })
      setObjectives(finalObjectives);
    }
  };

  const handleConstraintChange = (event) => {
    setRandomConstraint({ ...randomConstraint, [event.target.name]: event.target.checked });
  };

  React.useEffect(() => {
    if (isSaving) {
      savingTimeoutRef.current = setTimeout(() => setIsSaving(false), CONFIRM_DELAY)
    }
    return () => clearTimeout(savingTimeoutRef.current)
  }, [isSaving])

  React.useEffect(() => {
    updateServerStatus();
    statusIntervalRef.current = setInterval(
      updateServerStatus,
      UPDATE_INTERVAL
    );
    return () => clearInterval(statusIntervalRef.current);
  }, [currentMap]);

  React.useEffect(() => {
    if (currentMap) {
      setObjectives(generateObjectivesGrid(currentMap.map.orientation));
    }
  }, [currentMap]);

  if (currentMap && unifiedGamemodeName(currentMap.game_mode) === "skirmish") {
    return (
      (<Container>
        <Alert severity="error">
            <AlertTitle>Error</AlertTitle>
            <strong>{currentMap.pretty_name}</strong> - Skirmish mode cannot have the game layout changed!
        </Alert>
        <Skeleton variant="rectangular" height={650} />
        <Skeleton variant="rectangular" height={250} />
      </Container>)
    );
  }

  if (!objectives) {
    return (
      (<Container>
        <Skeleton variant="rectangular" height={30} />
        <Skeleton variant="rectangular" height={650} />
        <Skeleton variant="rectangular" height={250} />
      </Container>)
    );
  }

  return (
    <Container>
      <ActionPanel>
        <Button
          disabled={isSaving}
          startIcon={isSaving && <CircularProgress size={20} />}
          color="secondary"
          variant="outlined"
          size="small"
          onClick={handleChangeLayoutClick}
        >
          CONFIRM LAYOUT
        </Button>
        <Button
          variant="outlined"
          size="small"
          onClick={handleResetLayoutClick}
        >
          CLEAR LAYOUT
        </Button>
      </ActionPanel>
      {currentMap ? (
        <ObjectivesContainer>
          <MapWrapper>
            <MapImg
              src={getTacMapImageSrc(currentMap)}
              alt=""
              draggable={false}
            />
          </MapWrapper>
          <ObjectivesGrid>
            {objectives.flat().map((state, index) => {
              return (
                <ControlButton
                  key={`${index}${state}`}
                  onClick={() => handleSelectClick(index)}
                  disabled={isButtonDisabled(state, index)}
                  state={state}
                ></ControlButton>
              );
            })}
          </ObjectivesGrid>
        </ObjectivesContainer>
      ) : (
        <Skeleton width="100%" height={"100%"} />
      )}
      <Box>
        <Alert severity="info">
          If you do not select one or more objectives, they will be chosen randomly based on the following criteria:
        </Alert>
        <FormControl component="fieldset">
          <FormLabel component="legend">Optional criteria</FormLabel>
          <FormGroup>
            <FormControlLabel
              control={<Checkbox checked={randomConstraint["1"]} name={"1"} onChange={handleConstraintChange} />}
              label="Objectives must be adjacent"
            />
            <FormControlLabel
              control={<Checkbox checked={randomConstraint["2"]} name={"2"} onChange={handleConstraintChange} />}
              label="Objectives must not be aligned in a straight line"
            />
          </FormGroup>
        </FormControl>
      </Box>
    </Container>
  );
}

export default MapObjectives;
