import * as React from "react";
import IconButton from "@mui/material/IconButton";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import { Box, Divider, ListItemIcon, Paper, Stack, styled, Tooltip, Typography } from "@mui/material";
import { useAuth } from "@/hooks/useAuth";

const HorizontalActionMenu = styled(Stack)(({ theme }) => ({
  width: 'fit-content',
}));

/**
 * Displays a menu of actions that the user can perform on a player.
 * The provided actions are filtered based on the user's permissions.
 */
export function ActionMenu({
  handleActionClick,
  actionList,
  ...props
}) {
  const { permissions: user } = useAuth();
  const [anchorEl, setAnchorEl] = React.useState(null);
  const open = Boolean(anchorEl);
  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };

  const filteredActionList = React.useMemo(
    () => actionList.filter(hasPermission(user)),
    [actionList, user]
  );

  return (
    <Box {...props}>
      <IconButton
        aria-label="more"
        id="long-button"
        aria-controls={open ? "long-menu" : undefined}
        aria-expanded={open ? "true" : undefined}
        aria-haspopup="true"
        onClick={handleClick}
      >
        <MoreVertIcon />
      </IconButton>
      <Menu
        id="long-menu"
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
      >
        {filteredActionList.map((action) => (
          <MenuItem
            key={action.name}
            onClick={() => {
              handleClose();
              handleActionClick(action);
            }}
          >
            <ListItemIcon>{action.icon}</ListItemIcon>
            <Typography
              variant="inherit"
              sx={{ textDecoration: action.depraceted ? "line-through" : "" }}
            >
              {action.name[0].toUpperCase() + action.name.slice(1)}
            </Typography>
          </MenuItem>
        ))}
        {filteredActionList.length === 0 && (
          <MenuItem onClick={handleClose}>No actions available</MenuItem>
        )}
      </Menu>
    </Box>
  );
}

export function ActionPanel({
  handleActionClick,
  actionList,
  ...props
}) {
  const { permissions: user } = useAuth();

  const filteredActionList = React.useMemo(
    () => actionList.filter(hasPermission(user)),
    [actionList, user]
  );

  return (
    <HorizontalActionMenu direction={'row'}>
      {filteredActionList.map((action) => (
        <React.Fragment key={action.name}>
          <Divider orientation="vertical" flexItem />
          <Tooltip
            title={action.name[0].toUpperCase() + action.name.substring(1)}
          >
            <IconButton size="small" disableRipple sx={{ borderRadius: 0 }} onClick={() => handleActionClick(action)}>{action.icon}</IconButton>
          </Tooltip>
        </React.Fragment>
      ))}
      {filteredActionList.length === 0 && (
        <Paper sx={{ p: 1 }}>
          <Typography>No actions available</Typography>
        </Paper>
      )}
    </HorizontalActionMenu>
  );
}

function hasPermission(user) {
  return (action) => {
    if (!user.is_superuser && action.permission) {
      // example ["can_blacklist", "can_watch", "can_ban", "can_message", "can_comment"]
      // user needs to have all permissions in the array
      return action.permission.every((perm) =>
        user.permissions.some((userPerm) => userPerm.permission === perm)
      );
    }

    return true;
  };
}
