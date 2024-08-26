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
  Box,
  createStyles,
} from "@material-ui/core";
import Avatar from "@material-ui/core/Avatar";
import DeleteIcon from "@material-ui/icons/Delete";

const useStyles = makeStyles((theme) => createStyles({
  draggingListItem: {
    boxShadow: "rgba(6, 24, 44, 0.4) 0px 0px 0px 2px, rgba(6, 24, 44, 0.65) 0px 4px 6px -1px, rgba(255, 255, 255, 0.08) 0px 1px 0px 0px inset"
  },
  base: {
    borderBottom: `1px solid ${theme.palette.divider}`,
  },
}));

const getLabels = (layer) => {
  const labels = [];

  if (layer.game_mode === "offensive") {
    labels.push("offensive");
    if (
      layer.attackers == "allies"
    ) {
      labels.push("allies");
    } else {
      labels.push("axis");
    }
  } else if (
    layer.game_mode === "control" ||
    layer.game_mode === "phased" ||
    layer.game_mode === "majority"
  ) {
    labels.push("skirmish");
  } else {
    labels.push("warfare");
  }

  labels.push(layer.environment);
  return labels;
};

const labelsColors = {
  offensive: "primary",
  night: "secondary",
  dusk: "secondary",
  dawn: "secondary",
  rain: "secondary",
  overcast: "secondary",
  warfare: "default",
  allies: "primary",
  axis: "secondary",
  skirmish: "secondary",
};

const labelsVariant = {
  offensive: "default",
  night: "default",
  dusk: "default",
  dawn: "default",
  rain: "default",
  overcast: "default",
  warfare: "default",
  axis: "outlined",
  allies: "outlined",
  skirmish: "default",
};

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
            primary={
              <Box>
                <Typography variant="subtitle2">
                  {item.pretty_name}
                </Typography>
                <Box style={{ display: "flex", gap: "0.25rem", flexWrap: "wrap" }}>
                  {getLabels(item).map((type) => (
                    <Chip
                      key={index + type}
                      size="small"
                      variant={labelsVariant[type]}
                      color={labelsColors[type]}
                      label={type}
                    />
                  ))}
                </Box>
              </Box>
            }
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
