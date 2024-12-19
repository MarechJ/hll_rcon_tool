import { List, ListItem, ListItemButton, Box } from '@mui/material'
import { PopoverMenu } from '@/components/shared/PopoverMenu'
import GroupIcon from '@mui/icons-material/Groups'
import { Tooltip, Button } from '@mui/material'

/**
 * @typedef {Object} UnitOption
 * @property {string} team
 * @property {string} unit_name
 * @property {string} unit
 * @property {string} [leader]
 * @property {number} [count]
 */

/**
 * @param {Object} props
 * @param {Array<UnitOption>} props.unitOptions
 * @param {Function} props.onUnitSelect
 * @returns {JSX.Element}
 */
export const UnitSelectionMenu = ({ unitOptions, onUnitSelect }) => (
  <PopoverMenu
    id='unit-picker'
    description='Pick a squad to select all players in it'
    renderButton={(props) => (
      <Button {...props}>
        <Tooltip title='Select by squad'>
          <GroupIcon />
        </Tooltip>
      </Button>
    )}
  >
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
      {unitOptions.map((option) => (
        <ListItem
          key={`${option.team}-${option.unit_name}`}
          dense
          disableGutters
          sx={{ '& .MuiButtonBase-root': { opacity: 1 } }}
        >
          <ListItemButton onClick={() => onUnitSelect(option)}>
            <Box sx={{ display: 'flex', alignItems: 'center', overflow: 'hidden', px: 0, py: 0.25, gap: 1 }}>
              <img src={`/icons/teams/${option.team === 'axis' ? 'ger' : 'us'}.webp`} width={16} height={16} />
              <img src={`/icons/roles/${option.type}.png`} width={16} height={16} />
              <Box sx={{ overflow: 'hidden', whiteSpace: 'nowrap', textOverflow: 'ellipsis' }}>
                <Box component='span' fontWeight='bold' textTransform='uppercase'>
                  {option.unit}
                  {option.count ? ` (${option.count})` : ''}
                </Box>
                <Box component='span'>{option.leader ? ` - ${option.leader}` : ''}</Box>
              </Box>
            </Box>
          </ListItemButton>
        </ListItem>
      ))}
    </List>
  </PopoverMenu>
)
