import { useGlobalStore } from '@/hooks/useGlobalState'
import { Typography, Box } from '@mui/material'
import { styled } from '@mui/material/styles'

const connectionStatus = {
  none: 0,
  full: 1,
  backend: 2
}

const StatusText = styled(Typography, {
  shouldForwardProp: (prop) => prop !== 'status'
})(({ theme, status }) => ({
  '&:before': {
    content: "''",
    display: 'inline-block',
    width: theme.spacing(1.5),
    height: theme.spacing(1.5),
    borderRadius: '50%',
    backgroundColor:
      status === connectionStatus.full
        ? theme.palette.success.main
        : status === connectionStatus.backend
        ? theme.palette.warning.main
        : theme.palette.error.main,
    marginRight: theme.spacing(1)
  }
}))

/**
 * Display the connection status of the web app to the backend server and the game server
 * 0 - Green - Connected to both
 * 1 - Yellow - Connected to backend only
 * 2 - Red - Not connected to either
 */
const ConnectionStatus = () => {
  const backendConnected = useGlobalStore((state) => state.serverState)
  const gameConnected = useGlobalStore((state) => state.status)

  const status =
    backendConnected && gameConnected
      ? connectionStatus.full
      : backendConnected
      ? connectionStatus.backend
      : connectionStatus.none

  return (
    <Box>
      <StatusText variant='subtitle2' status={status}>
        {status === connectionStatus.full
          ? 'Connected'
          : status === connectionStatus.backend
          ? 'Game server not connected'
          : 'Disconnected'}
      </StatusText>
    </Box>
  )
}

export default ConnectionStatus
