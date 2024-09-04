import * as React from "react";

import ListItem from "@mui/material/ListItem";
import ListItemAvatar from "@mui/material/ListItemAvatar";
import ListItemText from "@mui/material/ListItemText";
import { ListItemSecondaryAction } from "@mui/material";
import { MapAvatar, MapDescription } from "./map-details";
import { styled } from '@mui/material/styles';

const StyledListItem = styled(ListItem)(({
  borderBottom: `1px solid gray`,
}))

export function MapListItem({ mapLayer, primary, secondary, renderAction, ...props }) {

  return (
    <StyledListItem {...props}>
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
    </StyledListItem>
  );
}
