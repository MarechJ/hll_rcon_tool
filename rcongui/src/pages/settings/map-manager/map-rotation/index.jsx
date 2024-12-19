import MapRotationSettings from './map-rotation-config'
import MapRotation from './map-rotation'
import { Typography } from '@mui/material'

function MapRotationConfig() {
  return (
    <>
      <MapRotation />
      <Typography variant='h6'>Other settings</Typography>
      <MapRotationSettings />
    </>
  )
}

export default MapRotationConfig
