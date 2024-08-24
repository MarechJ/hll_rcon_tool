import React from "react";
import Grid from "@material-ui/core/Grid";
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import Link from "@material-ui/core/Link";
import { Link as RouterLink } from "react-router-dom";
import Button from "@material-ui/core/Button";
import ServerStatus from "./server-status";
import Menu from "@material-ui/core/Menu";
import MenuItem from "@material-ui/core/MenuItem";
import { navMenus } from "./nav-data";
import { LoginBox } from "./login";

const initialMenuState = navMenus.reduce((state, menu) => {
  state[menu.name] = false;
  return state;
}, {});

// TODO: Make this reactive, it's causing the view on mobile to be bigger then it should
const Header = ({ classes }) => {
  const [openedMenu, setOpenedMenu] = React.useState(initialMenuState);
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handleOpenMenu = (name) => (event) => {
    setOpenedMenu({
      ...openedMenu,
      [name]: true,
    });
    setAnchorEl(event.currentTarget);
  };

  const handleCloseMenu = (name) => () => {
    setOpenedMenu({
      ...openedMenu,
      [name]: false,
    });
    setAnchorEl(null);
  };

  return (
    <Grid container>
      <div className={classes.grow}>
        <AppBar position="static" elevation={0} className={classes.appBar}>
          <Toolbar>
            <ServerStatus />
            <nav
              style={{
                display: "flex",
                flexGrow: 1,
                justifyContent: "start",
                padding: "0 2rem",
                gap: "0.5rem",
              }}
            >
              {navMenus.map((menu) => (
                <React.Fragment key={menu.name}>
                  <Button color="inherit" onClick={handleOpenMenu(menu.name)}>
                    {menu.name}
                  </Button>
                  <Menu
                    id={`${menu.name}-menu`}
                    anchorEl={anchorEl}
                    keepMounted
                    open={openedMenu[menu.name]}
                    onClose={handleCloseMenu(menu.name)}
                    PaperProps={{
                      style: {
                        minWidth: '20ch',
                      },
                    }}
                  >
                    {menu.links.map((link) => (
                      <MenuItem onClick={handleCloseMenu(menu.name)}>
                        <Link
                          variant="button"
                          color="inherit"
                          component={RouterLink}
                          to={link.to}
                          key={link.to}
                        >
                          {link.name}
                        </Link>
                      </MenuItem>
                    ))}
                  </Menu>
                </React.Fragment>
              ))}
            </nav>
            <LoginBox classes={classes} component={RouterLink} />
          </Toolbar>
        </AppBar>
      </div>
    </Grid>
  );
};

export default Header;
