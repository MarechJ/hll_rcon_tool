import * as React from 'react';
import IconButton from '@mui/material/IconButton';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import { Box, ListItemIcon, Typography } from '@mui/material';

export default function ActionMenu({ handleActionClick, actionList, ...props }) {
  const [anchorEl, setAnchorEl] = React.useState(null);
  const open = Boolean(anchorEl);
  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };

  return (
    <Box {...props}>
      <IconButton
        aria-label="more"
        id="long-button"
        aria-controls={open ? 'long-menu' : undefined}
        aria-expanded={open ? 'true' : undefined}
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
        {actionList.map((action) => (
          <MenuItem key={action.name} onClick={() => { handleClose(); handleActionClick(action) }}>
            <ListItemIcon>{action.icon}</ListItemIcon>
            <Typography variant="inherit">{action.name[0].toUpperCase() + action.name.slice(1)}</Typography>
          </MenuItem>
        ))}
      </Menu>
    </Box>
  );
}
