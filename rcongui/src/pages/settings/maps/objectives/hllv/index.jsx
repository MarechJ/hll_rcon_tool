import { useCallback, useMemo, useState } from "react";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import {
  Alert,
  Autocomplete,
  Box,
  Button,
  Checkbox,
  CircularProgress,
  Divider,
  FormControl,
  FormControlLabel,
  FormGroup,
  FormLabel,
  IconButton,
  InputLabel,
  Menu,
  MenuItem,
  Select,
  Stack,
  Tab,
  Tabs,
  TextField,
  Typography,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-toastify";
import { useGlobalStore } from "@/stores/global-state";
import { MapChangeDialog } from "../../MapChangeDialog";
import { MapDetailsCardCompact } from "../../MapDetailsCard";
import {
  mapsManagerMutationOptions,
  mapsManagerQueryKeys,
  mapsManagerQueryOptions,
} from "../../queries";
import { MapObjectivesPicker } from "../MapObjectivesPicker";
import {
  flip,
  generateObjectivesGrid,
  getSelectedObjectives,
  reduceToInts,
  unifiedGamemodeName,
} from "../helpers";

const DEFAULT_RANDOM_CONSTRAINTS = { 1: true, 2: false };
const GAME_MODE_ORDER = { warfare: 0, offensive: 1 };

const showMutationError = (error) => {
  toast.error(
    <div>
      <span>{error.name}</span>
      <p>{error.message}</p>
    </div>
  );
};

const layoutToGrid = (mapLayer, sectors = []) => {
  const grid = generateObjectivesGrid(mapLayer.map.orientation);
  const objectiveNames = mapLayer.map.objectives ?? [];
  const isHorizontal = mapLayer.map.orientation === "horizontal";

  sectors.forEach((objective, rowIndex) => {
    const objectiveIndex =
      typeof objective === "number"
        ? objective
        : objectiveNames[rowIndex]?.indexOf(objective);
    if (objectiveIndex === undefined || objectiveIndex < 0) return;

    if (isHorizontal) {
      grid[objectiveIndex + 1][rowIndex] = true;
    } else {
      grid[rowIndex][objectiveIndex + 1] = true;
    }
  });

  return grid;
};

function SavedLayouts({
  activeMapId,
  deletingMapId,
  layouts,
  mapsById,
  onChangeMap,
  onDelete,
  onEdit,
}) {
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedLayout, setSelectedLayout] = useState(null);

  const closeMenu = () => {
    setAnchorEl(null);
    setSelectedLayout(null);
  };

  const runAction = (action) => {
    const layout = selectedLayout;
    closeMenu();
    if (layout) action(layout);
  };

  return (
    <Box
      sx={{
        minWidth: 0,
        height: "100%",
        border: "1px solid",
        borderColor: "divider",
        borderRadius: 1,
        overflow: "hidden",
      }}
    >
      <Box sx={{ p: 1.5, borderBottom: "1px solid", borderColor: "divider" }}>
        <Typography variant="subtitle1" fontWeight={600}>
          Existing layouts
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {layouts.length} saved {layouts.length === 1 ? "layout" : "layouts"}
        </Typography>
      </Box>
      <Stack
        sx={{ p: 1, maxHeight: { xs: "none", md: 670 }, overflowY: "auto" }}
      >
        {layouts.length === 0 && (
          <Alert severity="info">No objective layouts have been saved.</Alert>
        )}
        {layouts.map((layout) => {
          const mapLayer = mapsById.get(layout.mapId);
          return (
            <Box
              key={layout.mapId}
              role="button"
              tabIndex={0}
              onClick={() => onEdit(layout)}
              onKeyDown={(event) => {
                if (event.target !== event.currentTarget) return;
                if (event.key === "Enter" || event.key === " ") {
                  event.preventDefault();
                  onEdit(layout);
                }
              }}
              sx={{
                display: "flex",
                alignItems: "center",
                gap: 1,
                p: 1,
                mb: 1,
                border: "1px solid",
                borderColor:
                  activeMapId === layout.mapId ? "primary.main" : "divider",
                borderRadius: 1,
                bgcolor:
                  activeMapId === layout.mapId
                    ? "action.selected"
                    : "background.paper",
                cursor: "pointer",
                "&:hover": { bgcolor: "action.hover" },
                "&:focus-visible": {
                  outline: "2px solid",
                  outlineColor: "primary.main",
                  outlineOffset: 1,
                },
              }}
            >
              <Box sx={{ flex: 1, minWidth: 0 }}>
                {mapLayer ? (
                  <MapDetailsCardCompact mapLayer={mapLayer} />
                ) : (
                  <Typography>{layout.mapId}</Typography>
                )}
              </Box>
              <IconButton
                size="small"
                aria-label={`Actions for ${
                  mapLayer?.pretty_name ?? layout.mapId
                }`}
                aria-haspopup="true"
                onClick={(event) => {
                  event.stopPropagation();
                  setAnchorEl(event.currentTarget);
                  setSelectedLayout(layout);
                }}
              >
                {deletingMapId === layout.mapId ? (
                  <CircularProgress size={20} />
                ) : (
                  <MoreVertIcon />
                )}
              </IconButton>
            </Box>
          );
        })}
      </Stack>
      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={closeMenu}>
        <MenuItem onClick={() => runAction(onEdit)}>
          <EditIcon fontSize="small" sx={{ mr: 1 }} />
          Edit
        </MenuItem>
        <MenuItem onClick={() => runAction(onDelete)}>
          <DeleteIcon fontSize="small" sx={{ mr: 1 }} />
          Delete
        </MenuItem>
        <Divider />
        <MenuItem
          disabled={!mapsById.has(selectedLayout?.mapId)}
          onClick={() => runAction(onChangeMap)}
        >
          <PlayArrowIcon fontSize="small" sx={{ mr: 1 }} />
          Change to map
        </MenuItem>
      </Menu>
    </Box>
  );
}

function LayoutEditor({
  activeMap,
  maps,
  objectives,
  onClear,
  onMapChange,
  onObjectiveClick,
  onObjectiveNamePick,
  onRandomConstraintChange,
  onSave,
  randomConstraints,
  saving,
}) {
  const objectiveNames = activeMap?.map.objectives ?? [];
  const sortedMaps = useMemo(() => {
    return [...maps].sort((firstMap, secondMap) => {
      const firstMode = unifiedGamemodeName(firstMap.game_mode);
      const secondMode = unifiedGamemodeName(secondMap.game_mode);
      const modeComparison =
        (GAME_MODE_ORDER[firstMode] ?? Number.MAX_SAFE_INTEGER) -
          (GAME_MODE_ORDER[secondMode] ?? Number.MAX_SAFE_INTEGER) ||
        firstMode.localeCompare(secondMode);
      return (
        modeComparison ||
        firstMap.pretty_name.localeCompare(secondMap.pretty_name)
      );
    });
  }, [maps]);
  const selectedObjectives = activeMap
    ? getSelectedObjectives(
        objectives,
        objectiveNames,
        activeMap.map.orientation
      )
    : [];

  return (
    <Box
      sx={{
        minWidth: 0,
        border: "1px solid",
        borderColor: "divider",
        borderRadius: 1,
        overflow: "hidden",
      }}
    >
      <Stack
        direction={{ xs: "column", sm: "row" }}
        spacing={1}
        sx={{ p: 1 }}
        alignItems={{ sm: "center" }}
      >
        <Autocomplete
          size="small"
          sx={{ flex: 1, minWidth: 220 }}
          options={sortedMaps}
          value={activeMap}
          groupBy={(mapLayer) => unifiedGamemodeName(mapLayer.game_mode)}
          getOptionLabel={(mapLayer) => mapLayer.pretty_name}
          isOptionEqualToValue={(option, value) => option.id === value.id}
          onChange={(_event, mapLayer) => onMapChange(mapLayer?.id ?? null)}
          renderInput={(params) => (
            <TextField {...params} label="Map" placeholder="Select map" />
          )}
        />
        <Stack direction="row" spacing={1} justifyContent="flex-end">
          <Button
            variant="outlined"
            color="error"
            onClick={onClear}
            disabled={!activeMap || saving}
            startIcon={<DeleteIcon />}
          >
            Clear
          </Button>
          <Button
            variant="contained"
            onClick={onSave}
            disabled={!activeMap || saving}
            startIcon={
              saving ? (
                <CircularProgress size={20} color="inherit" />
              ) : (
                <CheckCircleIcon />
              )
            }
          >
            Save layout
          </Button>
        </Stack>
      </Stack>
      <Divider />
      <Stack direction={{ xs: "column", lg: "row" }}>
        <Box
          sx={{
            flex: 1,
            minWidth: 0,
            display: "flex",
            justifyContent: "center",
          }}
        >
          <MapObjectivesPicker
            objectives={objectives}
            map={activeMap}
            onClick={onObjectiveClick}
            loading={false}
          />
        </Box>
        <Stack
          spacing={2}
          sx={{
            width: { xs: "100%", lg: 300 },
            p: 2,
            borderLeft: { lg: "1px solid" },
            borderTop: { xs: "1px solid", lg: "none" },
            borderColor: "divider",
          }}
        >
          <FormControl component="fieldset">
            <FormLabel component="legend">Select by name</FormLabel>
            <Stack spacing={1.5} sx={{ pt: 2 }}>
              {objectiveNames.map((names, index) => (
                <FormControl key={index} size="small" fullWidth>
                  <InputLabel>Objective #{index + 1}</InputLabel>
                  <Select
                    value={selectedObjectives[index] ?? "random"}
                    onChange={(event) =>
                      onObjectiveNamePick(
                        index,
                        names.indexOf(event.target.value)
                      )
                    }
                    label={`Objective #${index + 1}`}
                  >
                    <MenuItem value="random">Random</MenuItem>
                    {names.map((name) => (
                      <MenuItem key={name} value={name}>
                        {name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              ))}
            </Stack>
          </FormControl>
          <FormControl component="fieldset">
            <FormLabel component="legend">Random fields criteria</FormLabel>
            <FormGroup>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={randomConstraints[1]}
                    name="1"
                    onChange={onRandomConstraintChange}
                  />
                }
                label="Objectives must be adjacent"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={randomConstraints[2]}
                    name="2"
                    onChange={onRandomConstraintChange}
                  />
                }
                label="Objectives must not be aligned in a straight line"
              />
            </FormGroup>
          </FormControl>
        </Stack>
      </Stack>
    </Box>
  );
}

function HLLVMapObjectivesPage() {
  const queryClient = useQueryClient();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));
  const serverState = useGlobalStore((state) => state.serverState);
  const [mobileTab, setMobileTab] = useState(0);
  const [activeMapId, setActiveMapId] = useState(null);
  const [objectives, setObjectives] = useState(
    generateObjectivesGrid("horizontal")
  );
  const [randomConstraints, setRandomConstraints] = useState(
    DEFAULT_RANDOM_CONSTRAINTS
  );
  const [mapToConfirm, setMapToConfirm] = useState(null);
  const [deletingMapId, setDeletingMapId] = useState(null);

  const { data: maps = [] } = useQuery(
    mapsManagerQueryOptions.mapsWithObjectives()
  );
  const { data: layouts = [] } = useQuery(
    mapsManagerQueryOptions.gameLayouts()
  );

  const mapsById = useMemo(
    () => new Map(maps.map((mapLayer) => [mapLayer.id, mapLayer])),
    [maps]
  );
  const layoutsByMapId = useMemo(
    () => new Map(layouts.map((layout) => [layout.mapId, layout])),
    [layouts]
  );
  const activeMap = mapsById.get(activeMapId) ?? null;

  const activateMap = useCallback(
    (mapId, sectors) => {
      if (!mapId) {
        setActiveMapId(null);
        setObjectives(generateObjectivesGrid("horizontal"));
        return;
      }
      const mapLayer = mapsById.get(mapId);
      if (!mapLayer) return;
      const savedSectors = sectors ?? layoutsByMapId.get(mapId)?.sectors ?? [];
      setActiveMapId(mapId);
      setObjectives(layoutToGrid(mapLayer, savedSectors));
      if (isMobile) setMobileTab(1);
    },
    [isMobile, layoutsByMapId, mapsById]
  );

  const { mutate: saveLayout, isPending: isSaving } = useMutation({
    ...mapsManagerMutationOptions.saveGameLayout,
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: mapsManagerQueryKeys.gameLayouts,
      });
      toast.success(`Objective layout saved for ${activeMap?.pretty_name}.`);
    },
    onError: showMutationError,
  });

  const { mutate: removeLayout } = useMutation({
    ...mapsManagerMutationOptions.removeGameLayout,
    onMutate: (mapId) => setDeletingMapId(mapId),
    onSuccess: async (_response, mapId) => {
      await queryClient.invalidateQueries({
        queryKey: mapsManagerQueryKeys.gameLayouts,
      });
      if (mapId === activeMapId && activeMap) {
        setObjectives(generateObjectivesGrid(activeMap.map.orientation));
      }
      toast.success("Objective layout deleted.");
    },
    onError: showMutationError,
    onSettled: () => setDeletingMapId(null),
  });

  const { mutate: changeMap, isPending: isChangingMap } = useMutation({
    ...mapsManagerMutationOptions.changeMap,
    onSuccess: (response) => {
      queryClient.invalidateQueries({
        queryKey: mapsManagerQueryKeys.gameState,
      });
      toast.success(`Map has been changed to ${response.arguments.map_name}`, {
        toastId: "map-change-success",
      });
      setMapToConfirm(null);
    },
    onError: (error) => {
      showMutationError(error);
      setMapToConfirm(null);
    },
  });

  const handleObjectiveClick = (index) => {
    const targetIndex = index % 5;
    const targetRow = Math.floor(index / 5);
    setObjectives((previous) =>
      previous.map((row, rowIndex) =>
        row.map((value, columnIndex) =>
          rowIndex === targetRow && columnIndex === targetIndex ? !value : value
        )
      )
    );
  };

  const handleObjectiveNamePick = (row, index) => {
    if (!activeMap) return;
    const orientation = activeMap.map.orientation;
    const targetRow = orientation === "vertical" ? row : index + 1;
    const targetColumn = orientation === "vertical" ? index + 1 : row;

    setObjectives((previous) =>
      previous.map((gridRow, rowIndex) =>
        gridRow.map((value, columnIndex) => {
          if (value === null) return null;
          if (orientation === "vertical" && rowIndex === targetRow) {
            return index === -1 ? false : columnIndex === targetColumn;
          }
          if (orientation === "horizontal" && columnIndex === targetColumn) {
            return index === -1 ? false : rowIndex === targetRow;
          }
          return value;
        })
      )
    );
  };

  const handleSave = () => {
    if (!activeMap) return;
    const orientedGrid =
      activeMap.map.orientation === "horizontal"
        ? flip(objectives)
        : objectives;
    const randomConstraintValue = Object.entries(randomConstraints).reduce(
      (value, [constraint, enabled]) =>
        enabled ? value + Number(constraint) : value,
      0
    );

    saveLayout({
      map_name: activeMap.id,
      objectives: reduceToInts(orientedGrid),
      random_constraints: randomConstraintValue,
    });
  };

  const handleEdit = (layout) => activateMap(layout.mapId, layout.sectors);
  const handleChangeMap = (layout) =>
    setMapToConfirm(mapsById.get(layout.mapId) ?? null);

  const savedLayouts = (
    <SavedLayouts
      activeMapId={activeMapId}
      deletingMapId={deletingMapId}
      layouts={layouts}
      mapsById={mapsById}
      onChangeMap={handleChangeMap}
      onDelete={(layout) => removeLayout(layout.mapId)}
      onEdit={handleEdit}
    />
  );

  const editor = (
    <LayoutEditor
      activeMap={activeMap}
      maps={maps}
      objectives={objectives}
      onClear={() =>
        activeMap &&
        setObjectives(generateObjectivesGrid(activeMap.map.orientation))
      }
      onMapChange={activateMap}
      onObjectiveClick={handleObjectiveClick}
      onObjectiveNamePick={handleObjectiveNamePick}
      onRandomConstraintChange={(event) =>
        setRandomConstraints((previous) => ({
          ...previous,
          [event.target.name]: event.target.checked,
        }))
      }
      onSave={handleSave}
      randomConstraints={randomConstraints}
      saving={isSaving}
    />
  );

  return (
    <>
      <Box sx={{ py: 1 }}>
        <Typography variant="h5" gutterBottom>
          Map Objective Layouts
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Save an objective layout for any map. Saved layouts remain active as
          server settings until they are edited or deleted.
        </Typography>
      </Box>

      {isMobile ? (
        <>
          <Tabs
            value={mobileTab}
            onChange={(_event, value) => setMobileTab(value)}
            variant="fullWidth"
            sx={{ mb: 1 }}
          >
            <Tab label={`Existing layouts (${layouts.length})`} />
            <Tab label="Map grid & selects" />
          </Tabs>
          <Box hidden={mobileTab !== 0}>{savedLayouts}</Box>
          <Box hidden={mobileTab !== 1}>{editor}</Box>
        </>
      ) : (
        <Stack direction="row" spacing={1} alignItems="stretch">
          <Box sx={{ width: 300, flexShrink: 0 }}>{savedLayouts}</Box>
          <Box sx={{ flex: 1, minWidth: 0 }}>{editor}</Box>
        </Stack>
      )}

      <MapChangeDialog
        open={Boolean(mapToConfirm)}
        mapLayer={mapToConfirm}
        onClose={() => setMapToConfirm(null)}
        onConfirm={() => mapToConfirm && changeMap(mapToConfirm.id)}
        pending={isChangingMap}
        serverName={serverState?.name}
      />
    </>
  );
}

export default HLLVMapObjectivesPage;
