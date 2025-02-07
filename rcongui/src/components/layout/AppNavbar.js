import { styled } from "@mui/material/styles";
import AppBar from "@mui/material/AppBar";
import Stack from "@mui/material/Stack";
import MuiToolbar from "@mui/material/Toolbar";
import { tabsClasses } from "@mui/material/Tabs";
import MenuRoundedIcon from "@mui/icons-material/MenuRounded";
import SideMenuMobile from "./SideMenuMobile";
import MenuButton from "./MenuButton";
import NavbarBreadcrumbs from "./NavbarBreadcrumbs";
import { useState } from "react";
import { useMediaQuery, useTheme } from "@mui/system";
import ServerStatus from "../Header/server-status";
import { Box } from "@mui/material";
import { useAppStore } from "@/hooks/useAppState";

const Toolbar = styled(MuiToolbar)({
  width: "100%",
  padding: "12px",
  display: "flex",
  flexDirection: "column",
  alignItems: "start",
  justifyContent: "center",
  gap: "12px",
  flexShrink: 0,
  [`& ${tabsClasses.flexContainer}`]: {
    gap: "8px",
    p: "8px",
    pb: 0,
  },
});

const AppNavbarBase = ({ toggleDrawer, open, isSmallScreen }) => {
  return (
    <AppBar
      position="fixed"
      sx={{
        display: { xs: "auto", lg: "none" },
        boxShadow: 0,
        bgcolor: "background.paper",
        backgroundImage: "none",
        borderBottom: "1px solid",
        borderColor: "divider",
      }}
    >
      <Toolbar variant="regular">
        <Stack
          direction="row"
          sx={{
            alignItems: "center",
            flexGrow: 1,
            width: "100%",
          }}
        >
          <MenuButton aria-label="menu" onClick={toggleDrawer}>
            <MenuRoundedIcon />
          </MenuButton>
          <Box sx={{ overflow: "hidden" }}>
            {isSmallScreen && <ServerStatus compact={isSmallScreen || !open} />}
          </Box>
          <Stack
            direction="row"
            spacing={1}
            sx={{ justifyContent: "end", flexShrink: 0, flexGrow: 1, pl: 1 }}
          >
            <NavbarBreadcrumbs />
          </Stack>
        </Stack>
      </Toolbar>
    </AppBar>
  );
};

export default function AppNavbar() {
  const openDrawer = useAppStore((state) => state.openDrawer);
  const toggleDrawer = useAppStore((state) => state.toggleDrawer);
  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down("lg"));

  return (
    <>
      <AppNavbarBase
        open={openDrawer}
        toggleDrawer={toggleDrawer}
        isSmallScreen={isSmallScreen}
      />
      <SideMenuMobile
        open={isSmallScreen ? openDrawer : false}
        toggleDrawer={isSmallScreen ? toggleDrawer : () => {}}
      />
    </>
  );
}
