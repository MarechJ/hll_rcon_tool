import { List, ListItem, ListItemButton, Box, ListItemIcon, Checkbox, ListItemText, Badge } from '@mui/material'
import { PopoverMenu } from '@/components/shared/PopoverMenu'
import Person4Icon from '@mui/icons-material/Person4'
import { Tooltip, Button } from '@mui/material'
import { SearchInput } from '@/components/shared/SearchInput'
import { useSelectionMenu } from '@/hooks/useSelectionMenu'

/**
 * @param {Object} props
 * @param {Object} props.actionOptions
 * @param {Function} props.onActionSelect
 * @returns {JSX.Element}
 */
export const LogPlayerSelectionMenu = ({ actionOptions, onActionSelect }) => {
  const { search, setSearch, onOpen, onClose, hasSelected, filteredOptions } = useSelectionMenu(actionOptions)

  return (
    <PopoverMenu
      id='log-player-picker'
      description='Pick a player to filter the logs'
      onOpen={onOpen}
      onClose={onClose}
      renderButton={(props) => (
        <Button {...props}>
          <Tooltip title='Filter by player'>
            <Badge
              color='secondary'
              variant='dot'
              invisible={!hasSelected}
              anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
            >
              <Person4Icon />
            </Badge>
          </Tooltip>
        </Button>
      )}
    >
      <SearchInput value={search} onChange={(e) => setSearch(e.target.value)} />
      <List
        sx={{
          width: '100%',
          bgcolor: 'background.paper',
          position: 'relative',
          overflowY: 'auto',
          overflowX: 'hidden',
          maxHeight: 300,
          '& ul': { padding: 0 }
        }}
      >
        {filteredOptions.map((actionName) => (
          <ListItem key={`${actionName}`} dense disableGutters sx={{ '& .MuiButtonBase-root': { opacity: 1 } }}>
            <ListItemButton onClick={() => onActionSelect(actionName)}>
              <ListItemIcon>
                <Checkbox
                  edge='start'
                  checked={actionOptions[actionName]}
                  tabIndex={-1}
                  disableRipple
                  inputProps={{
                    'aria-labelledby': `picker-player-${actionName}`
                  }}
                />
              </ListItemIcon>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  overflow: 'hidden',
                  px: 0,
                  py: 0.25,
                  gap: 1
                }}
              >
                <Box
                  sx={{
                    overflow: 'hidden',
                    whiteSpace: 'nowrap',
                    textOverflow: 'ellipsis'
                  }}
                >
                  <ListItemText id={`picker-player-${actionName}`}>{actionName}</ListItemText>
                </Box>
              </Box>
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </PopoverMenu>
  )
}
