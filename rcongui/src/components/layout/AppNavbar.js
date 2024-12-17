import { styled } from '@mui/material/styles'
import AppBar from '@mui/material/AppBar'
import Stack from '@mui/material/Stack'
import MuiToolbar from '@mui/material/Toolbar'
import { tabsClasses } from '@mui/material/Tabs'
import MenuRoundedIcon from '@mui/icons-material/MenuRounded'
import SideMenuMobile from './SideMenuMobile'
import MenuButton from './MenuButton'
import NavbarBreadcrumbs from './NavbarBreadcrumbs'
import { useState } from 'react'

const Toolbar = styled(MuiToolbar)({
  width: '100%',
  padding: '12px',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'start',
  justifyContent: 'center',
  gap: '12px',
  flexShrink: 0,
  [`& ${tabsClasses.flexContainer}`]: {
    gap: '8px',
    p: '8px',
    pb: 0
  }
})

const AppNavbarBase = ({ toggleDrawer }) => {
  return (
    <AppBar
      position='fixed'
      sx={{
        display: { xs: 'auto', lg: 'none' },
        boxShadow: 0,
        bgcolor: 'background.paper',
        backgroundImage: 'none',
        borderBottom: '1px solid',
        borderColor: 'divider',
        top: '56px'
      }}
    >
      <Toolbar variant='regular'>
        <Stack
          direction='row'
          sx={{
            justifyContent: 'space-between',
            alignItems: 'center',
            flexGrow: 1,
            width: '100%'
          }}
        >
          <MenuButton aria-label='menu' onClick={toggleDrawer(true)}>
            <MenuRoundedIcon />
          </MenuButton>
          <Stack direction='row' spacing={1} sx={{ justifyContent: 'center' }}>
            <NavbarBreadcrumbs />
          </Stack>
        </Stack>
      </Toolbar>
    </AppBar>
  )
}

export default function AppNavbar() {
  const [open, setOpen] = useState(false)

  const toggleDrawer = (newOpen) => () => {
    setOpen(newOpen)
  }

  return (
    <>
      <AppNavbarBase toggleDrawer={toggleDrawer} />
      <SideMenuMobile open={open} toggleDrawer={toggleDrawer} />
    </>
  )
}
