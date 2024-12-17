import WbSunnyRoundedIcon from '@mui/icons-material/WbSunnyRounded'
import ModeNightRoundedIcon from '@mui/icons-material/ModeNightRounded'
import MenuButton from './MenuButton'

function ToggleColorMode({ mode, toggleColorMode, ...props }) {
  return (
    <MenuButton onClick={toggleColorMode} size='small' aria-label='button to toggle theme' {...props}>
      {mode === 'dark' ? <WbSunnyRoundedIcon fontSize='small' /> : <ModeNightRoundedIcon fontSize='small' />}
    </MenuButton>
  )
}

export default ToggleColorMode
