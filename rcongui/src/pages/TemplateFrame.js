import * as React from 'react';
import { createTheme, ThemeProvider, styled } from '@mui/material/styles';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import Box from '@mui/material/Box';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import ArrowBackRoundedIcon from '@mui/icons-material/ArrowBackRounded';
import ToggleColorMode from '@/components/dashboard-components/ToggleColorMode';
import getDashboardTheme from '@/themes/getDashboardTheme';
import ServerStatus from '../components/Header/server-status';
import ToggleWidthMode from '../components/dashboard-components/ToggleWidthMode';

const StyledAppBar = styled(AppBar)(({ theme }) => ({
  position: 'relative',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  flexShrink: 0,
  borderBottom: '1px solid',
  borderColor: theme.palette.divider,
  backgroundColor: theme.palette.background.paper,
  boxShadow: 'none',
  backgroundImage: 'none',
  zIndex: theme.zIndex.drawer + 1,
  flex: '0 0 auto',
}));

function TemplateFrame({
  toggleCustomTheme,
  mode,
  toggleColorMode,
  widthMode,
  toggleWidthMode,
  children,
}) {
  const handleChange = (event) => {
    toggleCustomTheme(event.target.value === 'custom');
  };
  const dashboardTheme = createTheme(getDashboardTheme(mode));

  return (
    <ThemeProvider theme={dashboardTheme}>
      <Box sx={{ height: '100dvh', display: 'flex', flexDirection: 'column' }}>
        <StyledAppBar>
          <Toolbar
            variant="dense"
            disableGutters
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              width: '100%',
              p: '8px 12px',
            }}
          >
            <ServerStatus />
            <Box sx={{ display: 'flex', gap: 1 }}>
              <ToggleWidthMode 
                mode={widthMode}
                toggleWidthMode={toggleWidthMode}
              />
              <ToggleColorMode
                data-screenshot="toggle-mode"
                mode={mode}
                toggleColorMode={toggleColorMode}
              />
            </Box>
          </Toolbar>
        </StyledAppBar>
        <Box sx={{ flex: '1 1', overflow: 'auto' }}>{children}</Box>
      </Box>
    </ThemeProvider>
  );
}

export default TemplateFrame;
