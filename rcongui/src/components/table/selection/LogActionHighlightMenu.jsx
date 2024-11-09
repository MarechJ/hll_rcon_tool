import {
  List,
  ListItem,
  ListItemButton,
  Box,
  ListItemIcon,
  Checkbox,
  ListItemText,
  ToggleButtonGroup,
  ToggleButton,
} from "@mui/material";
import { PopoverMenu } from "@/components/shared/PopoverMenu";
import AutoFixHighIcon from "@mui/icons-material/AutoFixHigh";
import { Tooltip, Button } from "@mui/material";
import { logActions } from "@/utils/lib";

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
}) => (
  <PopoverMenu
    id="log-action-highlight-picker"
    description="Pick an action to highlight its logs"
    renderButton={(props) => (
      <Button {...props}>
        <Tooltip title="Highlight action">
          <AutoFixHighIcon />
        </Tooltip>
      </Button>
    )}
  >
    <ToggleButtonGroup
      value={toggleValue === true ? "on" : "off"}
      size="small"
      exclusive
      onChange={(e, value) => {
        onToggle(value);
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
      {[
        ...Object.keys(actionOptions).sort((a, b) => {
          if (actionOptions[a] && actionOptions[b]) {
            // Both are selected, so compare them alphabetically
            return a.localeCompare(b);
          }

          if (actionOptions[a]) {
            // Only `a` is selected, move `a` up
            return -1;
          }

          if (actionOptions[b]) {
            // Only `b` is selected, move `b` up
            return 1;
          }

          // Neither is selected, so compare alphabetically
          return a.localeCompare(b);
        }),
      ].map((actionName) => (
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
