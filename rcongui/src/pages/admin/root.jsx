import * as React from 'react';
import { createTheme, ThemeProvider, alpha } from '@mui/material/styles';
import { Container, Box, Stack, CssBaseline } from '@mui/material';
import getDashboardTheme from '@/themes/getDashboardTheme';
import AppNavbar from '@/components/layout/AppNavbar';
import Header from '@/components/layout/Header';
import SideMenu from '@/components/layout/SideMenu';
import TemplateFrame from '@/pages/TemplateFrame';
import { ToastContainer } from "react-toastify";
import { defer, Outlet, redirect } from "react-router-dom";
import { useStorageState } from "@/hooks/useStorageState"
import { get } from '@/utils/fetchUtils';
import "react-toastify/dist/ReactToastify.css";
import { ActionDialogProvider } from '@/hooks/useActionDialog';
import { PlayerSidebarProvider } from '@/hooks/usePlayerSidebar';

const fetchResource = async (url, errorMessage) => {
  try {
    const response = await get(url);
    if (!response.ok) throw new Response(errorMessage, { status: 404 });
    const data = await response.json();
    if (!data.result) throw new Response(errorMessage, { status: 404 });
    return data.result;
  } catch (error) {
    console.warn(`Failed to fetch ${url}:`, error);
    return null; // Return null if any request fails
  }
};

export const action = async ({ request }) => {
  const { intent }  = Object.fromEntries(await request.formData());

  if (intent === 'logout') {
      const response = await get('logout');
      const data = await response.json();
      const success = data.result;

      if (!success) {
        throw data;
      }

      return redirect('/login')
  }
}

export const loader = async () => {
    try {
        const response = await get('is_logged_in');
        const data = await response.json();

        const authenticated = data.result.authenticated;

        if (!authenticated) {
            throw new Error('Not authenticated.')
        }

        const fetchUserPermissions = fetchResource(
          'get_own_user_permissions',
          'Failed to load own permissions.'
        )

        const fetchConnectionInfo = fetchResource(
          'get_connection_info',
          'Failed to load crcon connection info.'
        )

        const fetchOtherServers = fetchResource(
          'get_server_list',
          'Failed to load crcon server list.'
        )

          // Run all promises concurrently
        const [permissions, thisServer, otherServers] = await Promise.all([
          fetchUserPermissions,
          fetchConnectionInfo,
          fetchOtherServers,
        ]);

        return defer({ 
          permissions,
          thisServer,
          otherServers
        });

    } catch (error) {
        return redirect('/login')
    }
}

export default function Root() {
  const [mode, setMode] = useStorageState("crcon-mode", "dark");
  const [widthMode, setWidthMode] = useStorageState("crcon-width", "xl");
  const dashboardTheme = createTheme(getDashboardTheme(mode));

  const toggleColorMode = () => {
    const newMode = mode === 'dark' ? 'light' : 'dark';
    setMode(newMode);
  };

  const toggleWidthMode = () => {
    const newMode = widthMode === "xl" ? "false" : "xl"
    setWidthMode(newMode)
  }

  return (
    <TemplateFrame
      mode={mode}
      widthMode={widthMode}
      toggleColorMode={toggleColorMode}
      toggleWidthMode={toggleWidthMode}
    >
      <ThemeProvider theme={dashboardTheme}>
        <CssBaseline enableColorScheme />
        <Box sx={{ display: 'flex' }}>
          <SideMenu />
          <AppNavbar />
          {/* Main content */}
          <Box
            component="main"
            sx={(theme) => ({
              flexGrow: 1,
              backgroundColor: alpha(theme.palette.background.default, 1),
              overflow: 'auto',
            })}
          >
            <Stack
              spacing={2}
              sx={{
                alignItems: 'center',
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
