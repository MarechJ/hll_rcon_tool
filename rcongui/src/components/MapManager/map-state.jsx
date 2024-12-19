import { Box, Typography } from '@mui/material'
import { makeStyles } from '@mui/styles'
import Skeleton from '@mui/material/Skeleton'
import { MapDetail } from './map-details'

const useStyles = makeStyles((theme) => ({
  main: {
    maxWidth: theme.breakpoints.values.sm,
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing(1)
  },
  mapBoxContainer: {
    display: 'flex',
    alignItems: 'center',
    padding: theme.spacing(1),
    gap: theme.spacing(2)
  },
  divider: {
    height: 2,
    width: '100%',
    background: theme.palette.divider
  },
  dividerContainer: {
    flexGrow: 1
  },
  dividerText: {
    width: '100%',
    textAlign: 'center',
    display: 'block'
  }
}))

export function MapState({ gameState }) {
  const classes = useStyles()

  if (!gameState) {
    return <Skeleton variant='rectangular' height={60} />
  }

  return (
    <Box className={classes.mapBoxContainer}>
      <MapDetail mapLayer={gameState.current_map} />
      <Box className={classes.dividerContainer}>
        <Typography variant='caption' className={classes.dividerText}>
          Up next in {gameState.raw_time_remaining}
        </Typography>
        <Box className={classes.divider}></Box>
      </Box>
      <MapDetail mapLayer={gameState.next_map} />
    </Box>
  )
}
