import * as React from "react";
import { Draggable } from "react-beautiful-dnd";

import makeStyles from "@material-ui/core/styles/makeStyles";
import ListItem from "@material-ui/core/ListItem";
import ListItemAvatar from "@material-ui/core/ListItemAvatar";
import ListItemText from "@material-ui/core/ListItemText";
import {
  ListItemSecondaryAction,
  IconButton,
  Chip,
  Typography,
} from "@material-ui/core";
import Avatar from "@material-ui/core/Avatar";
import DeleteIcon from "@material-ui/icons/Delete";

const useStyles = makeStyles({
  draggingListItem: {
    background: "rgb(235,235,235)",
  },
  noDot: {
    listStyleType: "none",
  },
});

const DraggableListItem = ({ item, index, onRemove }) => {
  const getLabels = (layer) => {
    const labels = [];

    if (layer.game_mode === "offensive") {
      labels.push("offensive");
    } else if (
      layer.game_mode === "control" ||
      layer.game_mode === "phased" ||
      layer.game_mode === "majority"
    ) {
      labels.push("skirmish");
    } else {
      labels.push("warfare");
    }
    if (
      layer.map.allies.name == "us" ||
      layer.map.allies.name == "rus" ||
      layer.map.allies.name == "gb"
    ) {
      labels.push("allies");
    } else {
      labels.push("axis");
    }
    if (layer.environment !== "day") {
      labels.push("night");
    }
    return labels;
  };

  const labelsColors = {
    offensive: "primary",
    night: "secondary",
    warfare: "default",
    allies: "primary",
    axis: "secondary",
    skirmish: "secondary",
  };

  const labelsVariant = {
    offensive: "default",
    night: "default",
    warfare: "default",
    axis: "outlined",
    allies: "outlined",
    skirmish: "default",
  };

  const classes = useStyles();
  return (
    <Draggable draggableId={item.id + index} index={index}>
      {(provided, snapshot) => (
        <ListItem
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          className={
            snapshot.isDragging
              ? classes.draggingListItem + " " + classes.noDot
              : classes.noDot
          }
        >
          <ListItemAvatar>
            <Avatar src={`maps/${item.image_name}`} />
          </ListItemAvatar>
          <ListItemText
            primary={
              <>
                <Typography display="inline" variant="h6">
                  {item.pretty_name}{" "}
                  {getLabels(item).map((e) => (
                    <Chip
                      size="small"
                      variant={labelsVariant[e]}
                      color={labelsColors[e]}
                      label={e}
                    />
                  ))}
                </Typography>
              </>
            }
            secondary={<>{item.id}</>}
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
