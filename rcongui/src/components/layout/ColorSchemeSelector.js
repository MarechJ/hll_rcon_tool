import * as React from 'react';
import Button from '@mui/material/Button';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import ColorLensIcon from '@mui/icons-material/ColorLens';
import CheckIcon from '@mui/icons-material/Check';

export default function ColorSchemeSelector({ currentScheme, onSchemeChange, colorSchemes }) {
  const [anchorEl, setAnchorEl] = React.useState(null);
  const open = Boolean(anchorEl);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleSchemeSelect = (scheme) => {
    onSchemeChange(scheme);
    handleClose();
  };

  return (
    <React.Fragment>
      <Button
        onClick={handleClick}
        size="small"
        sx={{
          minWidth: 40,
          px: 1,
        }}
      >
        <ColorLensIcon />
      </Button>
      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        slotProps={{
          paper: {
            variant: 'outlined',
            elevation: 0,
            sx: {
              minWidth: 180,
              mt: 1,
            },
          },
        }}
      >
        {colorSchemes.map((scheme) => (
          <MenuItem
            key={scheme.value}
            selected={currentScheme === scheme.value}
            onClick={() => handleSchemeSelect(scheme.value)}
          >
            <ListItemIcon sx={{ visibility: currentScheme === scheme.value ? 'visible' : 'hidden' }}>
              <CheckIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>{scheme.name}</ListItemText>
          </MenuItem>
        ))}
      </Menu>
    </React.Fragment>
  );
} 