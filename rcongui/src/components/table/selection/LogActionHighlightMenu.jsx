import {
  Box,
  Button,
  Checkbox,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  ToggleButton,
  ToggleButtonGroup,
  Tooltip,
  Badge,
} from "@mui/material";
import { PopoverMenu } from "@/components/shared/PopoverMenu";
import AutoFixHighIcon from "@mui/icons-material/AutoFixHigh";
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
 * @returns {JSX.Element}
 */
export const LogActionHighlightMenu = ({
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
    filteredOptions,
    searchInputRef,
  } = useSelectionMenu(actionOptions);

  return (
    <PopoverMenu
      id="log-action-highlight-picker"
      description="Pick an action to highlight its logs"
      onOpen={onOpen}
      onClose={onClose}
      renderButton={(props) => (
      <Button {...props}>
        <Tooltip title="Highlight action">
          <Badge
            color="secondary"
            variant="dot"
            invisible={toggleValue === false}
            anchorOrigin={{ vertical: "top", horizontal: "right" }}
          >
            <AutoFixHighIcon />
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
      aria-label="logs table highlight change"
      fullWidth
    >
      <ToggleButton
        sx={{ borderRadius: 0 }}
        value="on"
        aria-label="highlighted table"
      >
        ON
      </ToggleButton>
      <ToggleButton
        sx={{ borderRadius: 0 }}
        value="off"
        aria-label="normal table"
      >
        OFF
      </ToggleButton>
    </ToggleButtonGroup>
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
      <SearchInput
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Search actions"
        ref={searchInputRef}
      />
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
