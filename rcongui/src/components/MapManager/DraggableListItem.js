import * as React from "react";
import { Draggable } from "react-beautiful-dnd";
import ListItem from "@mui/material/ListItem";
import ListItemAvatar from "@mui/material/ListItemAvatar";
import ListItemText from "@mui/material/ListItemText";
import { ListItemSecondaryAction, IconButton, Typography } from "@mui/material";
import Avatar from "@mui/material/Avatar";
import DeleteIcon from "@mui/icons-material/Delete";
import { MapDetails } from "./map-details";
import { styled } from '@mui/material/styles';

const StyledListItem = styled(Typography)(({ theme, isDrag }) => ({
  borderBottom: `1px solid gray`,
  ...(isDrag && {
    boxShadow: "rgba(6, 24, 44, 0.4) 0px 0px 0px 2px, rgba(6, 24, 44, 0.65) 0px 4px 6px -1px, rgba(255, 255, 255, 0.08) 0px 1px 0px 0px inset"
  })
}));

const DraggableListItem = ({ item, index, onRemove }) => {

  return (
    (<Draggable draggableId={item.id + index} index={index}>
      {(provided, snapshot) => (
        <StyledListItem
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          isDrag={snapshot.isDragging}
        >
          <ListItemAvatar>
            <Avatar src={`maps/${item.image_name}`} />
          </ListItemAvatar>
          <ListItemText
            primary={item.map.pretty_name}
            secondary={<MapDetails mapLayer={item} />}
          />
          <ListItemSecondaryAction>
            <IconButton
              edge="end"
              aria-label="delete"
              onClick={() => onRemove(index)}
              size="large">
              <DeleteIcon />
            </IconButton>
          </ListItemSecondaryAction>
        </StyledListItem>
      )}
    </Draggable>)
  );
};

export default DraggableListItem;
