import { createTheme, ThemeProvider, styled } from '@mui/material/styles'
import Box from '@mui/material/Box'
import AppBar from '@mui/material/AppBar'
import Toolbar from '@mui/material/Toolbar'
import ToggleColorMode from '@/components/layout/ToggleColorMode'
import getDashboardTheme from '@/themes/getDashboardTheme'
import ServerStatus from '@/components/Header/server-status'
import ToggleWidthMode from '@/components/layout/ToggleWidthMode'
import MenuRoundedIcon from '@mui/icons-material/MenuRounded'
import MenuButton from '@/components/layout/MenuButton'
import MenuOpenIcon from '@mui/icons-material/MenuOpen'

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
  flex: '0 0 auto'
}))

function TemplateFrame({ toggleDrawer, openDrawer, mode, toggleColorMode, widthMode, toggleWidthMode, children }) {
  const dashboardTheme = createTheme(getDashboardTheme(mode))

  return (
    <ThemeProvider theme={dashboardTheme}>
      <Box sx={{ height: '100dvh', display: 'flex', flexDirection: 'column' }}>
        <StyledAppBar>
          <Toolbar
            disableGutters
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              width: '100%',
              p: '8px 12px'
            }}
          >
            <MenuButton
              aria-label='toggle-menu'
              onClick={toggleDrawer}
              sx={{ display: { xs: 'none', lg: 'inline-flex' } }}
            >
              {!openDrawer ? <MenuRoundedIcon /> : <MenuOpenIcon />}
            </MenuButton>
            <Box
              sx={{
                display: 'flex',
                flexGrow: 1,
                gap: 1,
                overflowX: 'hidden',
                textOverflow: 'ellipsis',
                textWrap: 'nowrap'
              }}
            >
              <ServerStatus />
            </Box>
            <Box sx={{ display: 'flex', gap: 2, width: 'fit-content' }}>
              <ToggleWidthMode mode={widthMode} toggleWidthMode={toggleWidthMode} />
              <ToggleColorMode data-screenshot='toggle-mode' mode={mode} toggleColorMode={toggleColorMode} />
            </Box>
          </Toolbar>
        </StyledAppBar>
        <Box sx={{ flex: '1 1', overflow: 'auto' }}>{children}</Box>
      </Box>
    </ThemeProvider>
  )
}

export default TemplateFrame
