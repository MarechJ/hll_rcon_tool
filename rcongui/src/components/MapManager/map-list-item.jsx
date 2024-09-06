import * as React from "react";

import ListItem from "@mui/material/ListItem";
import ListItemAvatar from "@mui/material/ListItemAvatar";
import ListItemText from "@mui/material/ListItemText";
import { ListItemButton, ListItemSecondaryAction } from "@mui/material";
import { MapAvatar, MapDescription } from "./map-details";


export function MapListItem({ mapLayer, primary, secondary, renderAction, ...props }) {

  const ListItemComponent = props.button ? ListItemButton : ListItem;

  return (
    <ListItemComponent sx={{ borderBottom: `1px solid gray` }} {...props}>
      <ListItemAvatar>
        <MapAvatar mapLayer={mapLayer} />
      </ListItemAvatar>
      <ListItemText
        primary={primary ?? mapLayer.map.pretty_name}
        secondary={secondary ?? <MapDescription mapLayer={mapLayer} />}
      />
      {renderAction && (
        <ListItemSecondaryAction>
          {renderAction(mapLayer)}
        </ListItemSecondaryAction>
      )}
    </ListItemComponent>
  );
}
