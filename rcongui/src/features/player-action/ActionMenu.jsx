import IconButton from "@mui/material/IconButton";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import MoreHorizIcon from "@mui/icons-material/MoreHoriz";
import {
  Box,
  Divider,
  ListItemIcon,
  Paper,
  Stack,
  styled,
  Tooltip,
  Typography,
} from "@mui/material";
import { useAuth } from "@/hooks/useAuth";
import { useActionDialog } from "@/hooks/useActionDialog";
import { usePlayerSidebar } from "@/hooks/usePlayerSidebar";
import PersonIcon from "@mui/icons-material/Person";
import {useMemo, useState} from "react";

const HorizontalActionMenu = styled(Stack)(({ theme }) => ({
  width: "fit-content",
}));

/**
 * Displays a menu of actions that the user can perform on a player.
 * The provided actions are filtered based on the user's permissions.
 */
export function ActionMenu({
  handleActionClick,
  actionList,
  orientation = "vertical",
  ...props
}) {
  const { permissions: user } = useAuth();
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);
  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };

  const filteredActionList = useMemo(
    () => actionList.filter(hasPermission(user)),
    [actionList, user]
  );

  return (
    <Box>
      <IconButton
        aria-label="more"
        id="long-button"
        aria-controls={open ? "long-menu" : undefined}
        aria-expanded={open ? "true" : undefined}
        aria-haspopup="true"
        onClick={handleClick}
        {...props}
      >
        {orientation === "vertical" ? <MoreVertIcon /> : <MoreHorizIcon />}
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
            dense
          >
            <ListItemIcon>{action.icon}</ListItemIcon>
            <Typography
              variant="inherit"
              sx={{ textDecoration: action.deprecated ? "line-through" : "" }}
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

/**
 * @typedef {Object} Player
 * @property {string} player_id - The unique identifier for the player
 * @property {string} name - The name of the player
 */

/**
 * Displays a menu of actions that the user can perform on a player.
 * The provided actions are filtered based on the user's permissions.
 * If the withProfile prop is true, a profile button will be added to the menu.
 * The profile button will open the player sidebar with the player's id.
 * @param {Player|Player[]} recipients - The player or players to perform actions on.
 * @param {ReactNode} renderButton - A custom button to render instead of the default one.
 * @param {boolean} withProfile - Whether to include a profile button in the menu.
 * @param {string} orientation - The orientation of the menu. Can be "vertical" or "horizontal".
 * @param {object} props - Additional props to pass to the menu button.
 */
export function ActionMenuButton({
  actions,
  recipients,
  renderButton,
  orientation = "vertical",
  withProfile = false,
  ...props
}) {
  const { permissions: user } = useAuth();
  const { openDialog } = useActionDialog();
  const { openWithId } = usePlayerSidebar();
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleActionClick = (action) => {
    handleClose();
    openDialog(action, recipients);
  };

  const handleProfileClick = () => {
    handleClose();
    openWithId(recipients.player_id);
  };

  const filteredActionList = useMemo(
    () => actions.filter(hasPermission(user)),
    [actions, user]
  );

  const buttonProps = {
    "aria-label": "more",
    id: "default-action-menu-button",
    "aria-controls": open ? "default-action-menu-button" : undefined,
    "aria-expanded": open ? "true" : undefined,
    "aria-haspopup": "true",
    onClick: handleClick,
  };

  return (
    <Box>
      {renderButton ? (
        renderButton({ ...buttonProps })
      ) : (
        <IconButton {...buttonProps} {...props}>
          {orientation === "vertical" ? <MoreVertIcon /> : <MoreHorizIcon />}
        </IconButton>
      )}
      <Menu
        id="long-menu"
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        sx={{ maxHeight: (theme) => theme.typography.pxToRem(500) }}
      >
        {withProfile && !Array.isArray(recipients) && (
          <MenuItem onClick={handleProfileClick} dense>
            <ListItemIcon>
              <PersonIcon />
            </ListItemIcon>
            View Profile
          </MenuItem>
        )}
        {withProfile && !Array.isArray(recipients) && <Divider />}
        {filteredActionList.map((action) => (
          <MenuItem
            key={action.name}
            onClick={() => handleActionClick(action)}
            dense
          >
            <ListItemIcon>{action.icon}</ListItemIcon>
            <Typography
              variant="inherit"
              sx={{ textDecoration: action.deprecated ? "line-through" : "" }}
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
