import { List, ListItem, ListItemButton, Box, ListItemIcon, Checkbox, ListItemText, Badge } from '@mui/material'
import { PopoverMenu } from '@/components/shared/PopoverMenu'
import FilterListIcon from '@mui/icons-material/FilterList'
import { Tooltip, Button } from '@mui/material'
import { logActions } from '@/utils/lib'
import { useSelectionMenu } from '@/hooks/useSelectionMenu'
import { SearchInput } from '@/components/shared/SearchInput'

/**
 * @param {Object} props
 * @param {Object} props.actionOptions
 * @param {Function} props.onActionSelect
 * @returns {JSX.Element}
 */
export const LogActionSelectionMenu = ({ actionOptions, onActionSelect }) => {
  const { search, setSearch, onOpen, onClose, hasSelected, filteredOptions } = useSelectionMenu(actionOptions)

  return (
    <PopoverMenu
      id='log-action-picker'
      description='Pick an action to filter the logs'
      onOpen={onOpen}
      onClose={onClose}
      renderButton={(props) => (
        <Button {...props}>
          <Tooltip title='Filter by action'>
            <Badge
              color='secondary'
              variant='dot'
              invisible={!hasSelected}
              anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
            >
              <FilterListIcon />
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
                  inputProps={{ 'aria-labelledby': `picker-${actionName}` }}
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
                  <ListItemText id={`picker-${actionName}`}>
                    {logActions[actionName]}
                    {' - '}
                    {actionName}
                  </ListItemText>
                </Box>
              </Box>
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </PopoverMenu>
  )
}
