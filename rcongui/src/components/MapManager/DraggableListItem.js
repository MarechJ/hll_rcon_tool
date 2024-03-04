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
import { getMapName, getMapImageUrl } from "../Scoreboard/utils";

const useStyles = makeStyles({
  draggingListItem: {
    background: "rgb(235,235,235)",
  },
  noDot: {
    listStyleType: "none",
  },
});

const DraggableListItem = ({ item, index, onRemove }) => {

  const getLabels = (fullName) => {
    const labels = [];

    if (fullName.search("offensive") !== -1 || fullName.search("off") !== -1) {
      labels.push("offensive");
    } else if (fullName.toLowerCase().search('skirmish') !== -1) {
      labels.push('skirmish')
    }
    else {
      labels.push("warfare");
    }
    if (
      fullName.toLowerCase().endsWith("us") ||
      fullName.toLowerCase().endsWith("rus")
    ) {
      labels.push("allies");
    }
    if (fullName.toLowerCase().endsWith("ger")) {
      labels.push("axis");
    }
    if (fullName.toLowerCase().search("night") !== -1) {
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
    <Draggable draggableId={item + index} index={index}>
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
            <Avatar src={getMapImageUrl(item)} />
          </ListItemAvatar>
          <ListItemText
            primary={
              <>
                <Typography display="inline" variant="h6">
                  {getMapName(item)}{" "}
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
            secondary={<>{item}</>}
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
