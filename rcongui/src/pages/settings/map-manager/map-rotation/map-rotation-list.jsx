import * as React from "react";
import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";
import { makeStyles } from "@mui/styles";
import {
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Tooltip,
} from "@mui/material";
import Avatar from "@mui/material/Avatar";
import DeleteIcon from "@mui/icons-material/Delete";
import InputIcon from "@mui/icons-material/Input";
import { MapDescription } from "../../../../components/MapManager/map-details";
import { getMapLayerImageSrc } from "../../../../components/MapManager/helpers";

const useStyles = makeStyles((theme) => ({
  draggingListItem: {
    boxShadow:
      "rgba(6, 24, 44, 0.4) 0px 0px 0px 2px, rgba(6, 24, 44, 0.65) 0px 4px 6px -1px, rgba(255, 255, 255, 0.08) 0px 1px 0px 0px inset",
  },
  base: {
    borderBottom: `1px solid ${theme.palette.divider}`,
  },
  secondaryAction: {
    display: "flex",
    flexDirection: "row",
    gap: theme.spacing(2),
  },
}));

const DraggableList = React.memo(
  ({ maps, onDragEnd, onRemove, onChange, isSaved }) => {
    const classes = useStyles();

    return (
      <DragDropContext onDragEnd={onDragEnd}>
        <Droppable droppableId="droppable-list">
          {(provided) => (
            <List
              dense={true}
              ref={provided.innerRef}
              {...provided.droppableProps}
            >
              {maps.map((mapLayer, index, thisList) => (
                <Draggable draggableId={mapLayer.id + index} index={index}>
                  {(provided, snapshot) => (
                    <ListItem
                      ref={provided.innerRef}
                      {...provided.draggableProps}
                      {...provided.dragHandleProps}
                      className={
                        snapshot.isDragging
                          ? classes.draggingListItem
                          : classes.base
                      }
                    >
                      <ListItemAvatar>
                        <Avatar src={getMapLayerImageSrc(mapLayer)} />
                      </ListItemAvatar>
                      <ListItemText
                        primary={mapLayer.map.pretty_name}
                        secondary={<MapDescription mapLayer={mapLayer} />}
                      />
                      <ListItemSecondaryAction
                        className={classes.secondaryAction}
                      >
                        {thisList.findIndex(
                          (aMapLayer) => aMapLayer.id === mapLayer.id
                        ) === index && (
                          <Tooltip title={"Change map"}>
                            <span>
                              <IconButton
                                edge="end"
                                aria-label="set map"
                                disabled={!isSaved}
                                onClick={() => onChange(mapLayer)}
                                size="large"
                              >
                                <InputIcon />
                              </IconButton>
                            </span>
                          </Tooltip>
                        )}
                        <IconButton
                          edge="end"
                          aria-label="delete"
                          onClick={() => onRemove(index)}
                          size="large"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                  )}
                </Draggable>
              ))}
              {provided.placeholder}
            </List>
          )}
        </Droppable>
      </DragDropContext>
    );
  }
);

export default DraggableList;
