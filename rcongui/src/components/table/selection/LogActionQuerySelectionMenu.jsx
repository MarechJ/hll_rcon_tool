import { ButtonBase, styled } from "@mui/material";
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
import SettingsIcon from "@mui/icons-material/Settings";
import { logActions } from "@/utils/lib";

const Button = styled(ButtonBase)(({ theme }) => ({
  fontSize: 13,
  width: "100%",
  textAlign: "left",
  paddingBottom: 8,
  color: "#586069",
  fontWeight: 600,
  "&:hover,&:focus": {
    color: "#0366d6",
    ...theme.applyStyles("dark", {
      color: "#58a6ff",
    }),
  },
  "& span": {
    width: "100%",
  },
  "& svg": {
    width: 16,
    height: 16,
  },
  ...theme.applyStyles("dark", {
    color: "#8b949e",
  }),
}));

/**
 * @param {Object} props
 * @param {Array<String>} props.selectedActions
 * @param {Function} props.onActionSelect
 * @returns {JSX.Element}
 */
export const LogActionQuerySelectionMenu = ({ selectedActions, onActionSelect }) => (
  <PopoverMenu
    id="log-action-query-picker"
    description="Pick an action to filter the logs query"
    renderButton={(props) => (
      <Button disableRipple {...props}>
        <span>Select</span>
        <SettingsIcon />
      </Button>
    )}
  >
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
        ...Object.keys(logActions).sort((a, b) => {
          if (selectedActions.includes(a) && selectedActions.includes(b)) {
            // Both are selected, so compare them alphabetically
            return a.localeCompare(b);
          }

          if (selectedActions.includes(a)) {
            // Only `a` is selected, move `a` up
            return -1;
          }

          if (selectedActions.includes(b)) {
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
);
