import {
  Badge,
  Button,
  Tooltip,
  ToggleButton,
  ToggleButtonGroup,
} from "@mui/material";
import { PopoverMenu } from "@/components/shared/PopoverMenu";
import Groups2Icon from "@mui/icons-material/Groups2";

export const LogTeamSelectionMenu = ({ selectedTeams, onTeamSelect }) => {
  const hasSelected = selectedTeams.length > 0;

  const handleTeamToggle = (team) => {
    onTeamSelect(team);
  };

  return (
    <PopoverMenu
      id="log-team-picker"
      description="Filter logs by team"
      sx={{ width: 200 }}
      renderButton={(props) => (
        <Button {...props}>
          <Tooltip title="Filter by team">
            <Badge
              color="secondary"
              variant="dot"
              invisible={!hasSelected}
              anchorOrigin={{ vertical: "top", horizontal: "right" }}
            >
              <Groups2Icon />
            </Badge>
          </Tooltip>
        </Button>
      )}
    >
      <ToggleButtonGroup
        value={selectedTeams}
        onChange={(e, value) => {}}
        aria-label="team selection"
        sx={{
          display: "flex",
          flexDirection: "column",
          gap: 1,
          p: 1,
        }}
      >
        <ToggleButton
          value="Allies"
          selected={selectedTeams.includes("Allies")}
          onClick={() => handleTeamToggle("Allies")}
          sx={{
            display: "flex",
            gap: 1,
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <img
            src="/icons/teams/us.webp"
            width={16}
            height={16}
            alt="Allies"
          />
          Allies
        </ToggleButton>
        <ToggleButton
          value="Axis"
          selected={selectedTeams.includes("Axis")}
          onClick={() => handleTeamToggle("Axis")}
          sx={{
            display: "flex",
            gap: 1,
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <img
            src="/icons/teams/ger.webp"
            width={16}
            height={16}
            alt="Axis"
          />
          Axis
        </ToggleButton>
      </ToggleButtonGroup>
    </PopoverMenu>
  );
};
