import ListItem from '@mui/material/ListItem'
import ListItemAvatar from '@mui/material/ListItemAvatar'
import ListItemText from '@mui/material/ListItemText'
import { ListItemButton } from '@mui/material'
import { MapAvatar, MapDescription } from './map-details'

const ListItemComponent = ({ children, secondaryAction, asButton, ...props }) =>
  asButton ? (
    <ListItem secondaryAction={secondaryAction} disablePadding>
      <ListItemButton role={undefined} disableRipple dense {...props}>
        {children}
      </ListItemButton>
    </ListItem>
  ) : (
    <ListItem secondaryAction={secondaryAction} {...props}>
      {children}
    </ListItem>
  )

export function MapListItem({ mapLayer, primary, secondary, secondaryAction, asButton, ...props }) {
  return (
    <ListItemComponent secondaryAction={secondaryAction} asButton={asButton} {...props}>
      <ListItemAvatar>
        <MapAvatar mapLayer={mapLayer} />
      </ListItemAvatar>
      <ListItemText
        primary={primary ?? mapLayer.map.pretty_name}
        secondary={secondary ?? <MapDescription mapLayer={mapLayer} />}
      />
    </ListItemComponent>
  )
}
