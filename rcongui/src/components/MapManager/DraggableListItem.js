import * as React from "react";
import { Draggable } from "react-beautiful-dnd";

import makeStyles from "@material-ui/core/styles/makeStyles";
import ListItem from "@material-ui/core/ListItem";
import ListItemAvatar from "@material-ui/core/ListItemAvatar";
import ListItemText from "@material-ui/core/ListItemText";
import Avatar from "@material-ui/core/Avatar";
import InboxIcon from "@material-ui/icons/Inbox";
import map_to_pict from "../Scoreboard/utils";

const useStyles = makeStyles({
  draggingListItem: {
    background: "rgb(235,235,235)",
  },
});

const DraggableListItem = ({ item, index }) => {
    
  const getMapName = (fullName) => {
    const parts = fullName.split("_");
    if (parts && parts.length > 0) {
      return parts[0];
    }
    return "foy";
  };

  const classes = useStyles();
  return (
    <Draggable draggableId={item + index} index={index}>
      {(provided, snapshot) => (
        <ListItem
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          className={snapshot.isDragging ? classes.draggingListItem : ""}
        >
          <ListItemAvatar>
            <Avatar src={map_to_pict[getMapName(item)]} />
          </ListItemAvatar>
          <ListItemText primary={item} />
        </ListItem>
      )}
    </Draggable>
  );
};

export default DraggableListItem;
