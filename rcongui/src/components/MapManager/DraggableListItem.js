import * as React from "react";
import { Draggable } from "react-beautiful-dnd";

import makeStyles from "@material-ui/core/styles/makeStyles";
import ListItem from "@material-ui/core/ListItem";
import ListItemAvatar from "@material-ui/core/ListItemAvatar";
import ListItemText from "@material-ui/core/ListItemText";
import {
  ListItemSecondaryAction,
  IconButton,
  createStyles,
} from "@material-ui/core";
import Avatar from "@material-ui/core/Avatar";
import DeleteIcon from "@material-ui/icons/Delete";
import { MapDetail } from "./map-detail";

const useStyles = makeStyles((theme) => createStyles({
  draggingListItem: {
    boxShadow: "rgba(6, 24, 44, 0.4) 0px 0px 0px 2px, rgba(6, 24, 44, 0.65) 0px 4px 6px -1px, rgba(255, 255, 255, 0.08) 0px 1px 0px 0px inset"
  },
  base: {
    borderBottom: `1px solid ${theme.palette.divider}`,
  },
}));

const DraggableListItem = ({ item, index, onRemove }) => {
  const classes = useStyles();

  return (
    <Draggable draggableId={item.id + index} index={index}>
      {(provided, snapshot) => (
        <ListItem
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          className={
            snapshot.isDragging ? classes.draggingListItem : classes.base
          }
        >
          <ListItemAvatar>
            <Avatar src={`maps/${item.image_name}`} />
          </ListItemAvatar>
          <ListItemText
            primary={item.map.pretty_name}
            secondary={<MapDetail mapLayer={item} />}
          />
          <ListItemSecondaryAction>
            <IconButton
              edge="end"
              aria-label="delete"
              onClick={() => onRemove(index)}
            >
              <DeleteIcon />
            </IconButton>
          </ListItemSecondaryAction>
        </ListItem>
      )}
    </Draggable>
  );
};

export default DraggableListItem;
