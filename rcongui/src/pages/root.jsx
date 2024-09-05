import * as React from 'react';
import { styled, ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Toolbar from '@mui/material/Toolbar';
import Container from '@mui/material/Container';
import themes from '../themes';
import { Outlet } from 'react-router-dom';
import { useStorageState } from '../hooks/useStorageState';
import Header from '../components/Header'

const AppWrapper = styled('div')(() => ({ display: 'flex', flexDirection: 'column' }));

const Main = styled('main')(({ theme }) => ({
  backgroundColor:
    theme.palette.mode === 'light'
      ? theme.palette.grey[100]
      : theme.palette.grey[900],
  flexGrow: 1,
  display: 'flex',
  flexDirection: 'column',
  height: '100vh',
  overflowY: 'auto',
  overflowX: 'clip',
  position: 'relative',
}));

export default function Root() {
  const [theme] = useStorageState('crconTheme', 'Dark');

  const defaultTheme = themes[theme];

  return (
    <ThemeProvider theme={defaultTheme}>
            <AppWrapper>
              <CssBaseline />
              <Header />
              <Main>
                <Toolbar /> {/* To offset from the top  */}
                <Container sx={{ mt: 2, mb: 4, flexGrow: 1 }}>
                  <Outlet />
                </Container>
              </Main>
            </AppWrapper>
    </ThemeProvider>
  );
}