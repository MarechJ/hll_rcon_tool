import * as React from "react";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import GroupRemoveIcon from "@mui/icons-material/GroupRemove";
import {
  Box,
  Checkbox,
  CircularProgress,
  Divider,
  FormControl,
  FormControlLabel,
  FormLabel,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  Stack,
  Tooltip,
  Typography,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { teamsLiveQueryOptions } from "@/queries/teams-live-query";
import { gameQueryOptions } from "@/queries/game-query";
import { ReasonField } from "./fields/ReasonField";
import { useForm } from "react-hook-form";
import { cmd } from "@/utils/fetchUtils";
import ErrorIcon from "@mui/icons-material/Error";
import CheckIcon from "@mui/icons-material/Check";
import ErrorBrowser from "@/components/shared/ErrorBrowser";
import debug from "@/utils/debug";

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const logger = debug("DISBAND SQUAD DIALOG");

// Disband Squad Dialog with react-hook-form integration
export default function DisbandSquadDialog() {
  const UNASSIGNED = "unassigned";
  const [PENDING, ERROR, SUCCESS] = [0, 1, 2];
  const [dialogOpen, setDialogOpen] = React.useState(false);
  const cachedUnitOptions = React.useRef(null);
  const [pendingOptionStates, setPendingOptionStates] = React.useState(
    new Map()
  );
  const [errors, setErrors] = React.useState([]);
  const theme = useTheme();
  const mode = theme?.palette?.mode || "light";
  const fullScreen = useMediaQuery(theme.breakpoints.down("md"));
  const queryClient = useQueryClient();

  const roleSrc = (role, mode) =>
    mode === "light"
      ? `/icons/roles/${role}_black.png`
      : `/icons/roles/${role}.png`;

  const { data: teamData, refetch: refetchTeamData } = useQuery({
    ...teamsLiveQueryOptions,
  });

  const { data: gameState } = useQuery({
    ...gameQueryOptions.state(),
  });

  const { mutate: disbandSquad, isPending } = useMutation({
    mutationFn: async (data) =>
      cmd.DISBAND_SQUAD({
        payload: {
          team_name: data.team,
          squad_name: data.unit_name,
          reason: data.reason,
        },
        throwRouteError: false,
      }),
    onMutate: async (variables) => {
      queryClient.cancelQueries({ queryKey: [teamsLiveQueryOptions.queryKey] });
      logger(
        "Disbanding squad:",
        variables.id,
        "with reason:",
        variables.reason
      );
      setPendingOptionStates((prev) => {
        const newStates = new Map(prev);
        newStates.set(variables.id, PENDING);
        return newStates;
      });
    },
    onSuccess: async (data, variables) => {
      setPendingOptionStates((prev) => {
        const newStates = new Map(prev);
        newStates.set(variables.id, SUCCESS);
        return newStates;
      });
    },
    onError: async (error, variables) => {
      console.error(
        "Failed to disband squad:",
        variables.team,
        variables.unit_name,
        error
      );
      setPendingOptionStates((prev) => {
        const newStates = new Map(prev);
        newStates.set(variables.id, ERROR);
        return newStates;
      });
      setErrors((prev) => [...prev, error.message]);
    },
    onSettled: async (data, error, variables) => {
      await sleep(2000);
      await refetchTeamData();
      setPendingOptionStates((prev) => {
        const newStates = new Map(prev);
        newStates.delete(variables.id);
        return newStates;
      });
      cachedUnitOptions.current = null;
    },
  });

  const unitOptions = React.useMemo(() => {
    if (cachedUnitOptions.current) {
      return cachedUnitOptions.current;
    }
    const units = [];
    for (const team in teamData) {
      for (const unit_name in teamData[team].squads) {
        const unit = teamData[team].squads[unit_name];
        if (unit_name === UNASSIGNED) continue;
        units.push({
          team,
          faction: gameState?.current_map?.map?.[team]?.name,
          unit_name,
          type: unit.type,
          count: unit.players.length,
          leader:
            unit.players.find((player) =>
              ["officer", "tankcommander", "spotter"].includes(player.role)
            )?.name ?? "",
        });
      }
    }
    units.sort((a, b) =>
      `${a.team}-${a.unit_name}`.localeCompare(`${b.team}-${b.unit_name}`)
    );
    return units;
  }, [teamData, gameState, cachedUnitOptions.current]);

  const {
    handleSubmit,
    formState: { errors: formErrors },
    setValue,
    watch,
    ...formProps
  } = useForm({
    defaultValues: {
      reason: "",
      squads: [], // Array of selected squad IDs
    },
  });

  // Watch the squads field to get current selections
  const selectedSquads = watch("squads");

  // Convert array to Set for easier checking
  const selectedSquadsSet = new Set(selectedSquads);

  const getOptionId = (option) => `${option.team}-${option.unit_name}`;

  const getIdOption = (id) =>
    unitOptions.find((option) => getOptionId(option) === id);

  React.useEffect(() => {
    const availableOptions = new Set(
      unitOptions.map((option) => getOptionId(option))
    );
    // Filter out unavailable squads from selection
    const filteredSquads = selectedSquads.filter((id) =>
      availableOptions.has(id)
    );
    if (filteredSquads.length !== selectedSquads.length) {
      setValue("squads", filteredSquads);
    }
  }, [unitOptions, selectedSquads, setValue]);

  const handleDialogClickOpen = () => {
    clearSelection();
    setValue("reason", "");
    setPendingOptionStates(new Map());
    cachedUnitOptions.current = null;
    setErrors([]);
    setDialogOpen(true);
  };

  const clearSelection = (team) => {
    if (!team) {
      setValue("squads", []);
    } else {
      const filteredSquads = selectedSquads.filter(
        (id) => getIdOption(id)?.team !== team
      );
      setValue("squads", filteredSquads);
    }
  };

  const handleDialogClose = () => {
    setDialogOpen(false);
  };

  const handleUnitSelect = (option) => {
    const id = getOptionId(option);
    const newSquads = selectedSquadsSet.has(id)
      ? selectedSquads.filter((squadId) => squadId !== id)
      : [...selectedSquads, id];
    setValue("squads", newSquads);
  };

  const handleAllToggle = (team) => () => {
    const teamOptions = unitOptions.filter((option) => option.team === team);
    const teamSquadIds = teamOptions.map((option) => getOptionId(option));
    const selectedTeamSquads = selectedSquads.filter((id) =>
      teamSquadIds.includes(id)
    );

    let newSquads;
    if (
      selectedTeamSquads.length === 0 ||
      selectedTeamSquads.length < teamOptions.length
    ) {
      // Select all for this team
      const unselectedTeamSquads = teamSquadIds.filter(
        (id) => !selectedSquadsSet.has(id)
      );
      newSquads = [...selectedSquads, ...unselectedTeamSquads];
    } else {
      // Deselect all for this team
      newSquads = selectedSquads.filter((id) => !teamSquadIds.includes(id));
    }

    setValue("squads", newSquads);
  };

  const handleFormSubmit = (data) => {
    // Handle the form submission with selected squads
    logger("Form data:", data);
    cachedUnitOptions.current = unitOptions;
    setErrors([]);
    data.squads.forEach((id) =>
      disbandSquad({
        ...getIdOption(id),
        reason: data.reason,
        id,
      })
    );
  };

  return (
    <React.Fragment>
      <Tooltip title={"Disband Squad"}>
        <span>
          <IconButton
            color="primary"
            onClick={handleDialogClickOpen}
            disabled={unitOptions.length === 0}
          >
            <GroupRemoveIcon />
          </IconButton>
        </span>
      </Tooltip>
      <Dialog
        open={dialogOpen}
        fullScreen={fullScreen}
        onClose={handleDialogClose}
        slotProps={{
          paper: {
            component: "form",
            onSubmit: handleSubmit(handleFormSubmit),
          },
        }}
      >
        <DialogTitle>Disband Squad</DialogTitle>
        <DialogContent>
          <DialogContentText>
            {`This command will redeploy(10s) all affected players and free the squad slot(s) for reassignment.`}
          </DialogContentText>
          <Stack spacing={2} marginTop={2}>
            <Stack
              direction={"row"}
              divider={<Divider flexItem orientation="vertical" />}
            >
              {["allies", "axis"].map((team) => {
                const teamOptions = unitOptions.filter(
                  (option) => option.team === team
                ).length;
                const selectedTeamOptions = selectedSquads.filter(
                  (id) => getIdOption(id)?.team === team
                ).length;
                return (
                  <Stack minWidth={"50%"} maxWidth={"50%"}>
                    <FormControlLabel
                      label={
                        <Typography
                          variant="h6"
                          alignSelf={"center"}
                          textAlign={"center"}
                          width={"100%"}
                        >
                          {team.toUpperCase()}
                        </Typography>
                      }
                      sx={{ px: 3 }}
                      control={
                        <Checkbox
                          disabled={teamOptions === 0}
                          checked={
                            teamOptions !== 0 &&
                            teamOptions === selectedTeamOptions
                          }
                          indeterminate={
                            selectedTeamOptions > 0 &&
                            selectedTeamOptions < teamOptions
                          }
                          onClick={handleAllToggle(team)}
                        />
                      }
                    />
                    <Divider flexItem />
                    <List
                      key={team}
                      sx={{
                        width: "100%",
                        bgcolor: "background.paper",
                        position: "relative",
                        overflowY: "auto",
                        overflowX: "hidden",
                        maxHeight: fullScreen ? "unset" : 300,
                        "& ul": { padding: 0 },
                      }}
                    >
                      {teamOptions === 0 && (
                        <Typography variant="caption">
                          No squads available
                        </Typography>
                      )}
                      {teamOptions > 0 &&
                        unitOptions
                          .filter((option) => option.team === team)
                          .map((option) => {
                            let InteractiveComponent;

                            switch (
                              pendingOptionStates.get(getOptionId(option))
                            ) {
                              case PENDING:
                                InteractiveComponent = (
                                  <CircularProgress
                                    size={16}
                                    sx={{ fontSize: "1em", mx: 1 }}
                                  />
                                );
                                break;
                              case SUCCESS:
                                InteractiveComponent = (
                                  <CheckIcon
                                    sx={{ fontSize: "1em", mx: 1 }}
                                    color="success"
                                  />
                                );
                                break;
                              case ERROR:
                                InteractiveComponent = (
                                  <ErrorIcon
                                    sx={{ fontSize: "1em", mx: 1 }}
                                    color="warning"
                                  />
                                );
                                break;

                              default:
                                InteractiveComponent = (
                                  <Checkbox
                                    checked={selectedSquadsSet.has(
                                      getOptionId(option)
                                    )}
                                    onClick={(event) => {
                                      event.stopPropagation();
                                      handleUnitSelect(option);
                                    }}
                                    disabled={pendingOptionStates.size}
                                  />
                                );
                                break;
                            }

                            return (
                              <ListItem
                                key={getOptionId(option)}
                                dense
                                disableGutters
                                sx={{ "& .MuiButtonBase-root": { opacity: 1 } }}
                              >
                                <ListItemButton
                                  onClick={() => handleUnitSelect(option)}
                                >
                                  {InteractiveComponent}
                                  <Box
                                    sx={{
                                      display: "flex",
                                      alignItems: "center",
                                      overflow: "hidden",
                                      px: 0,
                                      py: 0.25,
                                      gap: 0.25,
                                    }}
                                  >
                                    <img
                                      src={`/icons/teams/${
                                        option.faction ??
                                        (option.team === "axis" ? "ger" : "us")
                                      }.webp`}
                                      width={16}
                                      height={16}
                                    />
                                    <img
                                      src={roleSrc(option.type, mode)}
                                      width={16}
                                      height={16}
                                    />
                                    <Box
                                      sx={{
                                        overflow: "hidden",
                                        whiteSpace: "nowrap",
                                        textOverflow: "ellipsis",
                                      }}
                                    >
                                      <Box
                                        component="span"
                                        fontWeight="bold"
                                        textTransform="uppercase"
                                      >
                                        {option.unit_name}
                                        {option.count
                                          ? ` (${option.count})`
                                          : ""}
                                      </Box>
                                      {option.leader && (
                                        <Box component="span">
                                          {` - ${option.leader}`}
                                        </Box>
                                      )}
                                    </Box>
                                    {!option.leader && (
                                      <Box
                                        component={"img"}
                                        src="/icons/ping.webp"
                                        alt="No Leader"
                                        title="Unit has no leader"
                                        width={16}
                                        height={16}
                                        sx={{ opacity: 0.7, ml: 0.5 }}
                                      />
                                    )}
                                  </Box>
                                </ListItemButton>
                              </ListItem>
                            );
                          })}
                    </List>
                  </Stack>
                );
              })}
            </Stack>
            {errors.length > 0 && (
              <ErrorBrowser errors={errors} onClose={() => setErrors([])} />
            )}
            <Divider flexItem sx={{ mb: 2 }} />
            <ReasonField
              errors={formErrors}
              setValue={setValue}
              {...formProps}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDialogClose}>Cancel</Button>
          <Button
            type="submit"
            disabled={
              isPending ||
              unitOptions.length === 0 ||
              selectedSquads.length === 0
            }
          >
            Confirm
          </Button>
        </DialogActions>
      </Dialog>
    </React.Fragment>
  );
}
