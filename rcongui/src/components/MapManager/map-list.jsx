import * as React from "react";
import { List } from "@mui/material";
import { MapListItem } from "./map-list-item";

export function MapList({ mapLayers, ...props }) {
  return (
    <List dense={true} {...props}>
      {mapLayers.map((mapLayer, index) => (
        <MapListItem key={`${index}#${mapLayer.id}`} mapLayer={mapLayer} />
      ))}
    </List>
  );
}
