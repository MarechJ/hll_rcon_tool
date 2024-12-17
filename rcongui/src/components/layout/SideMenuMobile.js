import Button from '@mui/material/Button'
import Divider from '@mui/material/Divider'
import Drawer, { drawerClasses } from '@mui/material/Drawer'
import Stack from '@mui/material/Stack'
import LogoutRoundedIcon from '@mui/icons-material/LogoutRounded'
import MenuContent from './MenuContent'
import SelectContent from './SelectContent'
import { Box, List, ListItem, ListItemText } from '@mui/material'
import { Form } from 'react-router-dom'
import { navMenus } from '../Header/nav-data'
import NewReleases from './NewReleases'
import ConnectionStatus from './ConnectionStatus'

const MobileDrawer = ({ open, toggleDrawer, children }) => {
  return (
    <Drawer
      anchor='left'
      open={open}
      onClose={toggleDrawer(false)}
      sx={{
        zIndex: (theme) => theme.zIndex.drawer + 1,
        [`& .${drawerClasses.paper}`]: {
          backgroundImage: 'none',
          backgroundColor: 'background.paper',
          minWidth: 240
        }
      }}
    >
      <Stack
        sx={{
          maxWidth: '70dvw',
          height: '100%'
        }}
      >
        {children}
      </Stack>
    </Drawer>
  )
}

function AdminSideMenuMobile({ open, toggleDrawer }) {
  return (
    <MobileDrawer open={open} toggleDrawer={toggleDrawer}>
      <Stack sx={{ flexGrow: 1 }}>
        <MenuContent navigationTree={navMenus} />
        <List dense>
          <ListItem>
            <ListItemText sx={{ marginLeft: -0.5 }} primary={<ConnectionStatus />} />
          </ListItem>
          <NewReleases />
        </List>
        <Divider />
        <Box
          sx={{
            display: 'flex',
            p: 1.5
          }}
        >
          <SelectContent />
        </Box>
        <Divider />
      </Stack>
      <Stack sx={{ p: 2 }}>
        <Form method={'POST'} action='/'>
          <Button
            type='submit'
            name='intent'
            value='logout'
            variant='outlined'
            fullWidth
            startIcon={<LogoutRoundedIcon />}
          >
            Logout
          </Button>
        </Form>
      </Stack>
    </MobileDrawer>
  )
}

export default AdminSideMenuMobile
