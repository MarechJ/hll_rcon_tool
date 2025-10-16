import * as React from "react";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import GroupRemoveIcon from "@mui/icons-material/GroupRemove";
import Popper from "@mui/material/Popper";
import {
  Box,
  ClickAwayListener,
  InputBase,
  List,
  ListItem,
  ListItemButton,
  MenuItem,
  Select,
  Stack,
  TextField,
  Tooltip,
  useTheme,
} from "@mui/material";
import Autocomplete, { autocompleteClasses } from "@mui/material/Autocomplete";
import { useQuery } from "@tanstack/react-query";
import { teamsLiveQueryOptions } from "@/queries/teams-live-query";
import { gameQueryOptions } from "@/queries/game-query";
import SettingsIcon from "@mui/icons-material/Settings";
import CloseIcon from "@mui/icons-material/Close";
import DoneIcon from "@mui/icons-material/Done";

// USE REACT FORM HOOK
// USE AUTOCOMPLETE FIELDS
// HANDLE MULTIPLE SQUADS AT ONCE
// DISPLAY SELECTED SQUADS as chips with remove buttons
// ENSURE { squadId, squadName } remains the same since its selection
// if this changes there has been some change and the user may
// accidentally disband the wrong squad
// probably refetch on submit and double check the values
// before commiting the command execution
export default function DisbandSquadDialog() {
  const UNASSIGNED = "unassigned"
  const [dialogOpen, setDialogOpen] = React.useState(false);
  const [value, setValue] = React.useState([]);
  const theme = useTheme();
  const mode = theme?.palette?.mode || "light";

  const roleSrc = (role, mode) =>
    mode === "light"
      ? `/icons/roles/${role}_black.png`
      : `/icons/roles/${role}.png`;

  const { data: teamData, isFetching: isFetchingTeamData } = useQuery({
    ...teamsLiveQueryOptions,
  });

  const { data: gameState, isFetching: isFetchingGameState } = useQuery({
    ...gameQueryOptions.state(),
  });

  const isLoading = isFetchingGameState || isFetchingTeamData;

  const unitOptions = React.useMemo(() => {
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
  }, [teamData, gameState]);

  console.log({unitOptions})

  const handleDialogClickOpen = () => {
    setDialogOpen(true);
  };

  const handleDialogClose = () => {
    setDialogOpen(false);
  };

  const handleUnitSelect = (option) => {
    console.log(option)
  }

  return (
    <React.Fragment>
      <Tooltip title="Disband Squad">
        <span>
          <Button
            color="primary"
            onClick={handleDialogClickOpen}
            size="small"
            startIcon={<GroupRemoveIcon />}
          >
            Disband
          </Button>
        </span>
      </Tooltip>
      <Dialog
        open={dialogOpen}
        onClose={handleDialogClose}
        slotProps={{
          paper: {
            component: "form",
            onSubmit: (event) => {
              event.preventDefault();
              // TODO
              handleDialogClose();
            },
          },
        }}
      >
        <DialogTitle>Disband Squad</DialogTitle>
        <DialogContent>
          <DialogContentText>
            {`This command will redeploy(10s) all affected players and free the squad slot for reassignment.`}
          </DialogContentText>
          <Stack>
          <List
        sx={{
          width: "100%",
          bgcolor: "background.paper",
          position: "relative",
          overflowY: "auto",
          overflowX: "hidden",
          maxHeight: 300,
          "& ul": { padding: 0 },
        }}
      >
        {unitOptions.map((option) => (
          <ListItem
            key={`${option.team}-${option.unit_name}`}
            dense
            disableGutters
            sx={{ "& .MuiButtonBase-root": { opacity: 1 } }}
          >
            <ListItemButton onClick={() => handleUnitSelect(option)}>
              <Box sx={{ display: "flex", alignItems: "center", overflow: "hidden", px: 0, py: 0.25, gap: 1 }}>
                <img
                  src={`/icons/teams/${option.faction ?? (option.team === "axis" ? "ger" : "us")}.webp`}
                  width={16}
                  height={16}
                />
                <img src={roleSrc(option.type, mode)} width={16} height={16} />
                <Box sx={{ overflow: "hidden", whiteSpace: "nowrap", textOverflow: "ellipsis" }}>
                  <Box component="span" fontWeight="bold" textTransform="uppercase">
                    {option.unit_name}{option.count ? ` (${option.count})` : ""}
                  </Box>
                  <Box component="span">{option.leader ? ` - ${option.leader}` : ""}</Box>
                </Box>
              </Box>
            </ListItemButton>
          </ListItem>
        ))}
      </List>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDialogClose}>Cancel</Button>
          <Button type="submit">
            Confirm
          </Button>
        </DialogActions>
      </Dialog>
    </React.Fragment>
  );
}
