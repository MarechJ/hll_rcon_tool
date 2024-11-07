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
  import Person4Icon from '@mui/icons-material/Person4';
  import { Tooltip, Button } from "@mui/material";
  
  /**
   * @param {Object} props
   * @param {Object} props.actionOptions
   * @param {Function} props.onActionSelect
   * @returns {JSX.Element}
   */
  export const LogPlayerSelectionMenu = ({ actionOptions, onActionSelect }) => (
    <PopoverMenu
      id="log-player-picker"
      description="Pick a player to filter the logs"
      renderButton={(props) => (
        <Button {...props}>
          <Tooltip title="Filter by player">
            <Person4Icon />
          </Tooltip>
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
                  inputProps={{ "aria-labelledby": `picker-player-${actionName}` }}
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
                  <ListItemText id={`picker-player-${actionName}`}>
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
  