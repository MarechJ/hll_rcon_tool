import { useEffect, useState } from "react";
import { MapObjectivesPicker } from "./MapObjectivesPicker";
import { useLoaderData } from "react-router-dom";
import {
  flip,
  generateObjectivesGrid,
  getSelectedObjectives,
  reduceToInts,
  unifiedGamemodeName,
} from "./helpers";
import {
  Box,
  Button,
  Checkbox,
  FormControl,
  FormControlLabel,
  FormGroup,
  FormLabel,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import { useGlobalStore } from "@/stores/global-state";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  mapsManagerMutationOptions,
  mapsManagerQueryOptions,
} from "../queries";
import { toast } from "react-toastify";

function MapObjectivesPage() {
  const initialData = useLoaderData();
  const [currentMap, setCurrentMap] = useState(
    initialData.gameState.current_map
  );
  const [objectives, setObjectives] = useState(
    generateObjectivesGrid(initialData.gameState.current_map.map.orientation)
  );
  const [randomConstraint, setRandomConstraint] = useState({
    1: true,
    2: false,
  });
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const serverState = useGlobalStore((state) => state.serverState);
  const gameState = useGlobalStore((state) => state.gameState);
  const { data: objectiveNames, refetch: refetchObjectiveNames } = useQuery({
    ...mapsManagerQueryOptions.objectives(),
    initialData: initialData.objectives,
  });

  const mapOrientation = currentMap.map.orientation;
  const selectedObjectives = getSelectedObjectives(
    objectives,
    objectiveNames,
    mapOrientation
  );

  const { refetch: refetchGameState } = useQuery({
    ...mapsManagerQueryOptions.gameState(),
    enabled: false,
  });

  const { mutate: changeObjectives } = useMutation({
    ...mapsManagerMutationOptions.changeObjectives,
    onSuccess: (response) => {
      const newObjectives = response.result;
      const finalObjectives = generateObjectivesGrid(mapOrientation);
      const isHorizontal = mapOrientation === "horizontal";
      // update the grid with the new objectives
      newObjectives.forEach((objective, rowIndex) => {
        const row = rowIndex;
        const col = objectiveNames[rowIndex].indexOf(objective);
        if (isHorizontal) {
          finalObjectives[col + 1][row] = true;
        } else {
          finalObjectives[row][col + 1] = true;
        }
      });
      setObjectives(finalObjectives);
      toast.success(`Objectives have been changed.`);
      setConfirmDialogOpen(false);
    },
    onError: (error) => {
      toast.error(
        <div>
          <span>{error.name}</span>
          <p>{error.message}</p>
        </div>
      );
      setConfirmDialogOpen(false);
    },
  });

  const handleConstraintChange = (event) => {
    setRandomConstraint({
      ...randomConstraint,
      [event.target.name]: event.target.checked,
    });
  };

  const handleObjectiveClick = (index) => {
    const targetIndex = index % 5; // 0
    const targetRow = Math.floor(index / 5); // 1
    setObjectives((prevObjectives) =>
      prevObjectives.map((row, rowIndex) =>
        row.map((item, itemIndex) =>
          rowIndex === targetRow && itemIndex === targetIndex ? !item : item
        )
      )
    );
  };

  const handleObjectiveNamePick = (row, index) => {
    const targetRow = mapOrientation === "vertical" ? row : index + 1;
    const targetCol = mapOrientation === "vertical" ? index + 1 : row;
    setObjectives((prevObjectives) => {
      const temp = prevObjectives.map((row, rowIndex) =>
        row.map((item, colIndex) => {
          // skip inactive fields
          if (item === null) return null;
          // prevent selecting multiple options
          if (mapOrientation === "vertical") {
            if (rowIndex === targetRow) {
              if (colIndex === targetCol) return true;
              return false;
            }
          } else {
            if (colIndex === targetCol) {
              if (rowIndex === targetRow) return true;
              return false;
            }
          }
          // if not in the targeted row/col, leave as is
          return item;
        })
      );
      return temp;
    });
  };

  const handleClearClick = () => {
    setObjectives(generateObjectivesGrid(currentMap.map.orientation));
  };

  const handleDialogConfirmationClick = async () => {
    // Fetch gameState again to check we're changing the right map
    // it will reset all states if that's not true
    await refetchGameState();

    const chosenObjectives = reduceToInts(
      objectives[1][0] !== null ? flip(objectives) : objectives
    );

    const constraintValue = Object.entries(randomConstraint).reduce(
      (acc, [value, used]) => {
        if (used) return acc + Number(value);
        return acc;
      },
      0
    );
    changeObjectives({
      objectives: chosenObjectives,
      random_constraints: constraintValue,
    });
  };

  const handleConfirmClick = () => {
    setConfirmDialogOpen(true);
  };

  // Watch for map changes
  // Reset states on map change
  useEffect(() => {
    const local = currentMap;
    const global = gameState?.current_map;
    // when globally stored map has not loaded yet
    if (!global) return;
    // when the map has not changed
    if (local.id === global.id) return;
    // otherwise
    toast.info(
      <div>
        <div>The map has changed!</div>
        <div>{`${local.pretty_name} -> ${global.pretty_name}`}</div>
      </div>
    );
    setCurrentMap(global);
    setObjectives(generateObjectivesGrid(global.map.orientation));
    setConfirmDialogOpen(false);
    refetchObjectiveNames();
  }, [currentMap, gameState?.current_map]);

  if (unifiedGamemodeName(currentMap.game_mode) === "skirmish") {
    throw new Error("skirmish")
  }

  return (
    <>
      <Box sx={{ py: 1 }}>
        <Typography variant="h5" gutterBottom>
          Map Objectives
        </Typography>
        <Typography variant="body2" gutterBottom color="textSecondary">
          Click on the map to select objectives. The map will instantly restart
          upon confirmation. You can only set objectives to currently running
          map. The objectives in the omitted lines will be selected at random.
        </Typography>
      </Box>
      <Stack direction={{ xs: "column", md: "row" }}>
        <Box sx={{ width: { xs: "100%", md: "50%" } }}>
          <MapObjectivesPicker
            objectives={objectives}
            map={currentMap}
            onClick={handleObjectiveClick}
            loading={(objectives === null) & (currentMap === null)}
          />
        </Box>
        <Stack
          direction={{ xs: "column-reverse", md: "column" }}
          sx={{ width: { xs: "100%", md: "50%" } }}
        >
          <Stack
            direction="row"
            spacing={1}
            justifyContent={"end"}
            alignItems={"center"}
            sx={{
              height: 50,
              p: 1,
              border: (theme) => `1px solid ${theme.palette.divider}`,
            }}
          >
            <Button
              variant="outlined"
              color="error"
              onClick={handleClearClick}
              startIcon={<DeleteIcon />}
            >
              Clear
            </Button>
            <Button
              variant="contained"
              color="primary"
              disabled={false}
              onClick={handleConfirmClick}
              startIcon={
                false ? (
                  <CircularProgress size={20} color="inherit" />
                ) : (
                  <CheckCircleIcon />
                )
              }
            >
              Confirm
            </Button>
          </Stack>
          <FormControl component="fieldset" sx={{ px: 1, mt: 1 }}>
            <FormLabel component="legend">Select by name</FormLabel>
            <Stack spacing={2} sx={{ py: 2 }}>
              {objectiveNames.map((names, index) => (
                <FormControl
                  key={`Objective #${index}`}
                  size="small"
                  sx={{ minWidth: 180 }}
                >
                  <InputLabel>Objective #{index + 1}</InputLabel>
                  <Select
                    value={selectedObjectives[index]}
                    onChange={(e) =>
                      handleObjectiveNamePick(
                        index,
                        names.indexOf(e.target.value)
                      )
                    }
                    label={`Objective #${index}`}
                  >
                    <MenuItem value="random" name={"objective"}>
                      Random
                    </MenuItem>
                    {names.map((name) => (
                      <MenuItem key={name} value={name} name={"objective"}>
                        {name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              ))}
            </Stack>
          </FormControl>
          <FormControl component="fieldset" sx={{ px: 1, mt: 1 }}>
            <FormLabel component="legend">Random fields criteria</FormLabel>
            <FormGroup>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={randomConstraint["1"]}
                    name={"1"}
                    onChange={handleConstraintChange}
                  />
                }
                label="Objectives must be adjacent"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={randomConstraint["2"]}
                    name={"2"}
                    onChange={handleConstraintChange}
                  />
                }
                label="Objectives must not be aligned in a straight line"
              />
            </FormGroup>
          </FormControl>
        </Stack>
      </Stack>
      {/* Confirmation Dialog */}
      <Dialog
        open={confirmDialogOpen}
        onClose={() => setConfirmDialogOpen(false)}
        fullWidth
        maxWidth="xs"
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle>
          <div>Change objectives</div>
          <div>Server: {serverState?.name || "this server"}</div>
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            This will immediately restart the map with the objectives listed
            below.
          </DialogContentText>
          <Box
            sx={{
              py: 1,
              px: 1,
              my: 1,
              border: (theme) => `1px solid ${theme.palette.divider}`,
              textAlign: "center",
            }}
          >
            <Typography fontSize={"1.25rem"}>
              {currentMap.pretty_name}
            </Typography>
            <Stack spacing={0.5}>
              {selectedObjectives.map((objName, index) => (
                <Typography key={`Objective #${index + 1}`}>
                  Objective #{index + 1} - {objName}
                </Typography>
              ))}
            </Stack>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmDialogOpen(false)} color="inherit">
            Cancel
          </Button>
          <Button
            onClick={handleDialogConfirmationClick}
            color="primary"
            variant="contained"
            startIcon={<CheckCircleIcon />}
          >
            Confirm
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

export default MapObjectivesPage;
