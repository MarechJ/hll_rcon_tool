import * as React from "react";

import makeStyles from "@material-ui/core/styles/makeStyles";
import ListItem from "@material-ui/core/ListItem";
import ListItemAvatar from "@material-ui/core/ListItemAvatar";
import ListItemText from "@material-ui/core/ListItemText";
import { ListItemSecondaryAction, createStyles } from "@material-ui/core";
import Avatar from "@material-ui/core/Avatar";
import { MapDetail } from "./map-detail";
import { getMapLayerImageSrc } from "./helpers";

const useStyles = makeStyles((theme) =>
  createStyles({
    root: {
      borderBottom: `1px solid ${theme.palette.divider}`,
    },
  })
);

export function MapListItem({ mapLayer, primary, secondary, renderAction, ...props }) {
  const classes = useStyles();
  const src = getMapLayerImageSrc(mapLayer);

  return (
    <ListItem className={classes.root} {...props}>
      <ListItemAvatar>
        <Avatar src={src} />
      </ListItemAvatar>
      <ListItemText
        primary={primary ?? mapLayer.map.pretty_name}
        secondary={secondary ?? <MapDetail mapLayer={mapLayer} />}
      />
      {renderAction && (
        <ListItemSecondaryAction>
          {renderAction(mapLayer)}
        </ListItemSecondaryAction>
      )}
    </ListItem>
  );
}
