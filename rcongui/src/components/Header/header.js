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
import { Box, createStyles, makeStyles } from "@material-ui/core";

const useStyles = makeStyles((theme) => createStyles({
  root: {
    display: "flex",
    flexGrow: 1,
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "start",
    padding: theme.spacing(0.25),
    minHeight: 0,
    gap: theme.spacing(0.25),
    [theme.breakpoints.up("md")]: {
      flexDirection: "row",
      justifyContent: "space-between",
      alignItems: "center",
      gap: theme.spacing(2),
      padding: theme.spacing(0.5),
    }
  },
  nav: {
    display: "flex",
    flexDirection: "row",
    flexGrow: 1,
    justifyContent: "space-between",
  },
}))

const initialMenuState = navMenus.reduce((state, menu) => {
  state[menu.name] = false;
  return state;
}, {});

// TODO: Make this reactive, it's causing the view on mobile to be bigger then it should
const Header = ({ classes }) => {
  const [openedMenu, setOpenedMenu] = React.useState(initialMenuState);
  const [anchorEl, setAnchorEl] = React.useState(null);
  const localClasses = useStyles()

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
      <AppBar position="static">
        <Toolbar className={localClasses.root}>
          <ServerStatus />
          <Box className={localClasses.nav}>
            <nav>
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
                      <MenuItem component={RouterLink} to={link.to} key={link.to} color="inherit" onClick={handleCloseMenu(menu.name)}>
                        {link.name}
                      </MenuItem>
                    ))}
                  </Menu>
                </React.Fragment>
              ))}
            </nav>
            <LoginBox classes={classes} component={RouterLink} />
          </Box>
        </Toolbar>
      </AppBar>
    </Grid>
  );
};

export default Header;
