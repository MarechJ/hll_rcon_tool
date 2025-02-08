import { Button, Stack, ToggleButton, ToggleButtonGroup } from "@mui/material";
import {
  List,
  ListItem,
  ListItemButton,
  Box,
  ListItemIcon,
  Checkbox,
  ListItemText,
} from "@mui/material";
import { PopoverMenu } from "@/components/shared/PopoverMenu";
import { logActions } from "@/utils/lib";
import { SearchInput } from "@/components/shared/SearchInput";
import { useSelectionMenu } from "@/hooks/useSelectionMenu";

function fromValue(v) {
  return v === true ? "on" : "off";
}

/**
 * @param {Object} props
 * @param {Array<String>} props.selectedActions
 * @param {Function} props.onActionSelect
 * @returns {JSX.Element}
 */
export const LogActionQuerySelectionMenu = ({
  actionOptions,
  selectedActions,
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
    <Stack spacing={1}>
      <ToggleButtonGroup
        value={fromValue(toggleValue)}
        size="small"
        exclusive
        onChange={(e, value) => {
          if (value === null) {
            return;
          }
          onToggle(value === "on" ? true : false);
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
      <PopoverMenu
        id="log-action-query-picker"
        description="Pick an action to filter the logs query"
        onOpen={handleOpen}
        onClose={onClose}
        renderButton={(props) => (
          <Button variant="outlined" fullWidth disableRipple color="inherit" {...props}>
            Open Selection
          </Button>
        )} 
      >
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
                    checked={selectedActions.includes(actionName)}
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
    </Stack>
  );
};
