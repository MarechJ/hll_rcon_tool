import SmartToyIcon from "@mui/icons-material/SmartToy";
import {
  Badge,
  Box,
  Button,
  ToggleButton,
  ToggleButtonGroup,
  Tooltip,
} from "@mui/material";
import { PopoverMenu } from "@/components/shared/PopoverMenu";

const options = [
  { value: "include", label: "Show all" },
  { value: "only", label: "Only AutoMod" },
  { value: "exclude", label: "Hide AutoMod" },
];

export const AutoModFilterMenu = ({ value = "include", onSelect }) => {
  const hasCustomFilter = value !== "include";

  const handleChange = (_, newValue) => {
    if (newValue) {
      onSelect?.(newValue);
    }
  };

  return (
    <PopoverMenu
      id="automod-filter-menu"
      description="Filter log lines authored by AutoMod scripts"
      renderButton={(props) => (
        <Button {...props}>
          <Tooltip title="Filter AutoMod logs">
            <Badge
              color="secondary"
              variant="dot"
              invisible={!hasCustomFilter}
              anchorOrigin={{ vertical: "top", horizontal: "right" }}
            >
              <SmartToyIcon />
            </Badge>
          </Tooltip>
        </Button>
      )}
    >
      <Box sx={{ p: 1 }}>
        <ToggleButtonGroup
          exclusive
          fullWidth
          size="small"
          orientation="vertical"
          value={value}
          onChange={handleChange}
        >
          {options.map((option) => (
            <ToggleButton key={option.value} value={option.value}>
              {option.label}
            </ToggleButton>
          ))}
        </ToggleButtonGroup>
      </Box>
    </PopoverMenu>
  );
};
