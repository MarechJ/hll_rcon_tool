import Grid from "@mui/material/Grid2";
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import { Link as RouterLink } from "react-router-dom";
import Button from "@mui/material/Button";
import ServerStatus from "./server-status";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import { navMenus } from "./nav-data";
import { LoginBox } from "./login";
import { styled } from "@mui/material/styles";
import {Fragment, useState} from "react";

const StyledToolbar = styled(Toolbar)(({ theme }) => ({
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
}));

const Nav = styled('div')({
  display: "flex",
  flexDirection: "row",
  flexGrow: 1,
  justifyContent: "space-between",
});

const initialMenuState = navMenus.reduce((state, menu) => {
  state[menu.name] = false;
  return state;
}, {});

// TODO: Make this reactive, it's causing the view on mobile to be bigger then it should
const Header = () => {
  const [openedMenu, setOpenedMenu] = useState(initialMenuState);
  const [anchorEl, setAnchorEl] = useState(null);

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
        <StyledToolbar>
          <ServerStatus />
          <Nav>
            <nav>
              {navMenus.map((menu) => (
                <Fragment key={menu.name}>
                  <Button onClick={handleOpenMenu(menu.name)}>
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
                      <MenuItem component={RouterLink} to={link.to} key={link.to} onClick={handleCloseMenu(menu.name)}>
                        {link.name}
                      </MenuItem>
                    ))}
                  </Menu>
                </Fragment>
              ))}
            </nav>
            <LoginBox component={RouterLink} />
          </Nav>
        </StyledToolbar>
      </AppBar>
    </Grid>
  );
};

export default Header;
