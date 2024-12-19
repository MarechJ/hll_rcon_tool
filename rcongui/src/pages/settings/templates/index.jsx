import { Link, Outlet, useLocation } from 'react-router-dom'
import {
  Avatar,
  Box,
  ListItemAvatar,
  ListItemText,
  ListSubheader,
  MenuItem,
  Select,
  selectClasses
} from '@mui/material'
import ChatIcon from '@mui/icons-material/Chat'
import WavingHandIcon from '@mui/icons-material/WavingHand'
import AnnouncementIcon from '@mui/icons-material/Announcement'
import PodcastsIcon from '@mui/icons-material/Podcasts'
import SettingsSuggestIcon from '@mui/icons-material/SettingsSuggest'

const categories = [
  {
    name: 'Message',
    href: '/settings/templates/message',
    icon: <ChatIcon />
  },
  {
    name: 'Reason',
    href: '/settings/templates/reason',
    icon: <AnnouncementIcon />
  },
  {
    name: 'Welcome',
    href: '/settings/templates/welcome',
    icon: <WavingHandIcon />
  },
  {
    name: 'Broadcast',
    href: '/settings/templates/broadcast',
    icon: <PodcastsIcon />
  },
  {
    name: 'Auto-Settings',
    href: '/settings/templates/auto_settings',
    icon: <SettingsSuggestIcon />
  }
]

const MessagesRoot = () => {
  const location = useLocation()

  return (
    <Box>
      <Select
        labelId='messages-select'
        id='messages-simple-select'
        value={location.pathname}
        displayEmpty
        inputProps={{ 'aria-label': 'Select messages' }}
        fullWidth
        MenuProps={{
          PaperProps: {
            sx: {
              '& .MuiMenuItem-root:not(:last-child)': {
                mb: 1
              }
            }
          }
        }}
        sx={{
          maxHeight: 56,
          borderBottomLeftRadius: 0,
          borderBottomRightRadius: 0,
          '&.MuiList-root': {
            p: '8px'
          },
          [`& .${selectClasses.select}`]: {
            display: 'flex',
            alignItems: 'center',
            gap: '2px',
            pl: 1
          }
        }}
      >
        <ListSubheader sx={{ pt: 0 }}>Categories</ListSubheader>
        {categories?.map((type) => (
          <MenuItem key={type.name} value={type.href} component={Link} href={type.href} to={type.href}>
            <ListItemAvatar>
              <Avatar alt={type.name}>{type.icon}</Avatar>
            </ListItemAvatar>
            <ListItemText
              sx={{
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap'
              }}
              primary={type.name}
            />
          </MenuItem>
        ))}
      </Select>
      <Outlet />
    </Box>
  )
}

export default MessagesRoot
