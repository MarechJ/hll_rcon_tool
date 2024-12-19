import { Avatar, Box, Typography } from '@mui/material'
import { styled } from '@mui/material/styles'
import { getMapLayerImageSrc, unifiedGamemodeName } from './helpers'

const DescriptionRoot = styled('span')(({ theme }) => ({
  display: 'flex',
  flexWrap: 'wrap',
  gap: theme.spacing(0.5),
  textTransform: 'capitalize'
}))

const MapBox = styled(Box)(({ theme }) => ({
  display: 'flex',
  gap: theme.spacing(1),
  alignItems: 'center'
}))

const StyledAvatar = styled(Avatar)(({ theme }) => ({
  display: 'none',
  [theme.breakpoints.up('sm')]: {
    display: 'block'
  }
}))

export function MapDescription({ mapLayer }) {
  const gameMode = unifiedGamemodeName(mapLayer.game_mode)

  return (
    <DescriptionRoot>
      <Typography variant='caption'>{gameMode}</Typography>
      {gameMode === 'offensive' && (
        <>
          {' | '}
          <Typography variant='caption'>{mapLayer.attackers}</Typography>
        </>
      )}
      {' | '}
      <Typography variant='caption'>{mapLayer.environment}</Typography>
    </DescriptionRoot>
  )
}

export function MapAvatar({ mapLayer, ...props }) {
  return <Avatar src={getMapLayerImageSrc(mapLayer)} {...props} />
}

export function MapDetail({ mapLayer }) {
  return (
    <MapBox>
      <MapAvatar mapLayer={mapLayer} component={StyledAvatar} />
      <Box>
        <Typography variant='subtitle1'>{mapLayer.map.pretty_name}</Typography>
        <MapDescription mapLayer={mapLayer} />
      </Box>
    </MapBox>
  )
}
