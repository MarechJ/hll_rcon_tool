import React from "react";
import { Button, Menu, MenuItem } from "@mui/material";
import Grid from "@mui/material/Grid2";

const ChangeMap = ({ availableMaps, changeMap }) => {
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  return (
    (<Grid container size={12}>
      <Grid size={12}>
        <Button
          variant="outlined"
          color="primary"
          aria-controls="simple-menu"
          aria-haspopup="true"
          onClick={handleClick}
        >
          Change Map Now
        </Button>
        <Menu
          id="simple-menu"
          anchorEl={anchorEl}
          keepMounted
          open={Boolean(anchorEl)}
          onClose={handleClose}
        >
          {availableMaps.map((m) => (
            <MenuItem
              key={m.pretty_name}
              onClick={() => {
                changeMap(m.id).then(handleClose);
              }}
            >
              {m.pretty_name}
            </MenuItem>
          ))}
        </Menu>
      </Grid>
    </Grid>)
  );
};

export default ChangeMap;
