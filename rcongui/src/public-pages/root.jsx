import * as React from "react";
import { createTheme, ThemeProvider, alpha } from "@mui/material/styles";
import { Container, Box, Stack, CssBaseline } from "@mui/material";
import getDashboardTheme from "@/themes/getDashboardTheme";
import { PublicAppNavbar } from "@/components/layout/AppNavbar";
import Header from "@/components/layout/Header";
import TemplateFrame from "@/pages/TemplateFrame";
import { Outlet } from "react-router-dom";
import { useStorageState } from "@/hooks/useStorageState";
import { MenuDrawer } from "@/components/layout/SideMenu";
import MenuContent from "@/components/layout/MenuContent";
import { publicNavMenus } from "@/components/Header/nav-data";

export default function PublicRoot() {
  const [mode, setMode] = useStorageState("mode", "dark");
  const [widthMode, setWidthMode] = useStorageState("width", "xl");
  const dashboardTheme = createTheme(getDashboardTheme(mode));
  const [openDrawer, setOpenDrawer] = React.useState(true);

  const toggleDrawer = () => {
    setOpenDrawer((prev) => !prev);
  };

  const toggleColorMode = () => {
    const newMode = mode === "dark" ? "light" : "dark";
    setMode(newMode);
  };

  const toggleWidthMode = () => {
    const newMode = widthMode === "xl" ? "false" : "xl";
    setWidthMode(newMode);
  };

  return (
    <TemplateFrame
      mode={mode}
      widthMode={widthMode}
      toggleColorMode={toggleColorMode}
      toggleWidthMode={toggleWidthMode}
      toggleDrawer={toggleDrawer}
      openDrawer={openDrawer}
    >
      <ThemeProvider theme={dashboardTheme}>
        <CssBaseline enableColorScheme />
        <Box sx={{ display: "flex" }}>
          <MenuDrawer open={openDrawer}>
            <MenuContent navigationTree={publicNavMenus} />
          </MenuDrawer>
          <PublicAppNavbar />
          {/* Main content */}
          <Box
            component="main"
            sx={(theme) => ({
              flexGrow: 1,
              backgroundColor: alpha(theme.palette.background.default, 1),
              overflow: "auto",
            })}
          >
            <Stack
              spacing={2}
              sx={{
                alignItems: "center",
                px: 0,
                pb: 10,
                mt: { xs: 8, lg: 0 },
              }}
            >
              <Header />
              <Container maxWidth={widthMode} sx={{ overflowY: "auto", overflowX: "hidden" }}>
                <Outlet />
              </Container>
            </Stack>
          </Box>
        </Box>
      </ThemeProvider>
    </TemplateFrame>
  );
}
