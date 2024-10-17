import * as React from "react";
import { createTheme, ThemeProvider, alpha } from "@mui/material/styles";
import { Container, Box, Stack, CssBaseline } from "@mui/material";
import getDashboardTheme from "@/themes/getDashboardTheme";
import AppNavbar from "@/components/layout/AppNavbar";
import Header from "@/components/layout/Header";
import SideMenu from "@/components/layout/SideMenu";
import TemplateFrame from "@/pages/TemplateFrame";
import { ToastContainer } from "react-toastify";
import { defer, Outlet, redirect } from "react-router-dom";
import { useStorageState } from "@/hooks/useStorageState";
import { cmd, get } from "@/utils/fetchUtils";
import "react-toastify/dist/ReactToastify.css";
import { ActionDialogProvider } from "@/hooks/useActionDialog";
import { PlayerSidebarProvider } from "@/hooks/usePlayerSidebar";

export const loader = async () => {
  const thisServer = cmd.GET_GAME_SERVER_CONNECTION()
  const otherServers = cmd.GET_GAME_SERVER_LIST()

  return defer({
    thisServer,
    otherServers,
  });
};

export const action = async ({ request }) => {
  const { intent } = Object.fromEntries(await request.formData());

  if (intent === "logout") {
    const success = await cmd.LOGOUT();

    if (success) {
      return redirect("/login");
    }

  }
};

export default function Root() {
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
          <SideMenu open={openDrawer} />
          <AppNavbar />
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
                mx: 3,
                pb: 10,
                mt: { xs: 8, lg: 0 },
              }}
            >
              <Header />
              <Container maxWidth={widthMode}>
                <ActionDialogProvider>
                  <PlayerSidebarProvider>
                    <Outlet />
                  </PlayerSidebarProvider>
                </ActionDialogProvider>
              </Container>
            </Stack>
          </Box>
        </Box>
        <ToastContainer />
      </ThemeProvider>
    </TemplateFrame>
  );
}
