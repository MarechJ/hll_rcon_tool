import {
  List,
  ListItem,
  ListItemButton,
  Box,
  ListItemIcon,
  Checkbox,
  ListItemText,
  Badge,
} from "@mui/material";
import { PopoverMenu } from "@/components/shared/PopoverMenu";
import FilterListIcon from "@mui/icons-material/FilterList";
import { Tooltip, Button, ToggleButton, ToggleButtonGroup } from "@mui/material";
import { logActions } from "@/utils/lib";
import { useSelectionMenu } from "@/hooks/useSelectionMenu";
import { SearchInput } from "@/components/shared/SearchInput";

function fromValue(v) {
  return v === true ? "on" : "off";
}

/**
 * @param {Object} props
 * @param {Object} props.actionOptions
 * @param {Function} props.onActionSelect
 * @param {Function} props.onToggle
 * @param {string} props.toggleValue
 * @returns {JSX.Element}
 */
export const LogActionSelectionMenu = ({
  actionOptions,
  onActionSelect,
  onToggle,
  toggleValue,
}) => {
  const {
    search,
    setSearch,
    onOpen,
    onClose,
    hasSelected,
    filteredOptions,
    searchInputRef,
  } = useSelectionMenu(actionOptions);

  const handleOpen = () => {
    onOpen();
  };

  return (
    <PopoverMenu
      id="log-action-picker"
      description="Pick an action to filter the logs"
      onOpen={handleOpen}
      onClose={onClose}
      renderButton={(props) => (
        <Button {...props}>
          <Tooltip title="Filter by action">
            <Badge
              color="secondary"
              variant="dot"
              invisible={toggleValue === false}
              anchorOrigin={{ vertical: "top", horizontal: "right" }}
            >
              <FilterListIcon />
            </Badge>
          </Tooltip>
        </Button>
      )}
    >
      <ToggleButtonGroup
        value={fromValue(toggleValue)}
        size="small"
        exclusive
        onChange={(e, value) => {
          onToggle(value === null ? fromValue(toggleValue) : value);
        }}
        aria-label="logs table filter by action"
        fullWidth
      >
        <ToggleButton
          sx={{ borderRadius: 0 }}
          value="on"
          aria-label="filter by action"
        >
          ON
        </ToggleButton>
        <ToggleButton
          sx={{ borderRadius: 0 }}
          value="off"
          aria-label="filter by action"
        >
          OFF
        </ToggleButton>
      </ToggleButtonGroup>
      <SearchInput
        ref={searchInputRef}
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />
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
        {filteredOptions.map((actionName) => (
          <ListItem
            key={`${actionName}`}
            dense
            disableGutters
            sx={{ "& .MuiButtonBase-root": { opacity: 1 } }}
          >
            <ListItemButton onClick={() => onActionSelect(actionName)}>
              <ListItemIcon>
                <Checkbox
                  edge="start"
                  checked={actionOptions[actionName]}
                  tabIndex={-1}
                  disableRipple
                  inputProps={{ "aria-labelledby": `picker-${actionName}` }}
                />
              </ListItemIcon>
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  overflow: "hidden",
                  px: 0,
                  py: 0.25,
                  gap: 1,
                }}
              >
                <Box
                  sx={{
                    overflow: "hidden",
                    whiteSpace: "nowrap",
                    textOverflow: "ellipsis",
                  }}
                >
                  <ListItemText id={`picker-${actionName}`}>
                    {logActions[actionName]}
                    {" - "}
                    {actionName}
                  </ListItemText>
                </Box>
              </Box>
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </PopoverMenu>
  );
};
