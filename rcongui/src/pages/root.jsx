import * as React from "react";
import { Container, Box, Stack, CssBaseline, alpha } from "@mui/material";
import AppNavbar from "@/components/layout/AppNavbar";
import Header from "@/components/layout/Header";
import SideMenu from "@/components/layout/SideMenu";
import { ToastContainer } from "react-toastify";
import { Outlet, redirect } from "react-router-dom";
import { useStorageState } from "@/hooks/useStorageState";
import { cmd } from "@/utils/fetchUtils";
import "react-toastify/dist/ReactToastify.css";
import { ActionDialogProvider } from "@/hooks/useActionDialog";
import { PlayerSidebarProvider } from "@/hooks/usePlayerSidebar";
import AppTheme from "@/themes/AppTheme";

export const loader = async () => {
  return null;
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

const schemes = [
  { name: 'Default', value: 'default' },
  { name: 'GitHub', value: 'github' },
  { name: 'Lime', value: 'lime' },
  { name: 'High Contrast', value: 'highContrast' },
];

export default function Root() {
  const [mode, setMode] = useStorageState("mode", "dark");
  const [widthMode, setWidthMode] = useStorageState("width", "xl");
  const [colorScheme, setColorScheme] = useStorageState("colorScheme", "default");
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

  const onColorSchemeChange = (scheme) => {
    setColorScheme(scheme);
  };

  return (
    <AppTheme selectedScheme={colorScheme}>
      <CssBaseline enableColorScheme />
      <Box sx={{ display: "flex" }}>
        <SideMenu open={openDrawer} />
        <AppNavbar />
        {/* Main content */}
        <Box
          component="main"
          sx={(theme) => ({
            flexGrow: 1,
            backgroundColor: theme.vars
              ? `rgba(${theme.vars.palette.background.defaultChannel} / 1)`
              : alpha(theme.palette.background.default, 1),
            overflow: "auto",
          })}
        >
          <Stack
            spacing={2}
            sx={{
              alignItems: "center",
              mx: 3,
              pb: 5,
              mt: { xs: 8, lg: 0 },
            }}
          >
            <Header
              widthMode={widthMode}
              toggleWidthMode={toggleWidthMode}
              mode={mode}
              toggleColorMode={toggleColorMode}
              toggleDrawer={toggleDrawer}
              openDrawer={openDrawer}
              colorScheme={colorScheme}
              onColorSchemeChange={onColorSchemeChange}
              colorSchemes={schemes}
            />
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
    </AppTheme>
  );
}
