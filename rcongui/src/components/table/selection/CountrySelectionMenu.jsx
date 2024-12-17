import { List, ListItem, ListItemButton, Box } from '@mui/material'
import { CountryFlag } from '@/components/shared/CountryFlag'
import { PopoverMenu } from '@/components/shared/PopoverMenu'
import FlagIcon from '@mui/icons-material/Flag'
import { Tooltip, Button } from '@mui/material'

/**
 * @typedef {Object} CountryOption
 * @property {string} country
 * @property {number} [count]
 */

/**
 * @param {Object} props
 * @param {Array<CountryOption>} props.countryOptions
 * @param {Function} props.onCountrySelect
 * @returns {JSX.Element}
 */
export const CountrySelectionMenu = ({ countryOptions, onCountrySelect }) => (
  <PopoverMenu
    id='country-picker'
    description='Pick a country to select all players from it'
    renderButton={(props) => (
      <Button {...props}>
        <Tooltip title='Select by country'>
          <FlagIcon />
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
      {countryOptions.map((option) => (
        <ListItem key={option.country} dense disableGutters sx={{ '& .MuiButtonBase-root': { opacity: 1 } }}>
          <ListItemButton onClick={() => onCountrySelect(option)}>
            <Box sx={{ display: 'flex', alignItems: 'center', overflow: 'hidden', px: 0, py: 0.25, gap: 1 }}>
              <CountryFlag country={option.country} />
              <Box sx={{ overflow: 'hidden', whiteSpace: 'nowrap', textOverflow: 'ellipsis' }}>
                <Box component='span' fontWeight='bold' textTransform='uppercase'>
                  {option.country} - {option.count ? ` (${option.count})` : ''}
                </Box>
              </Box>
            </Box>
          </ListItemButton>
        </ListItem>
      ))}
    </List>
  </PopoverMenu>
)
