import * as React from "react";
import DraggableListItem from "./DraggableListItem";
import {
  DragDropContext,
  Droppable,
} from "react-beautiful-dnd";
import { List } from "@mui/material";

const DraggableList = React.memo(({ items, onDragEnd, onRemove }) => {
  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <Droppable droppableId="droppable-list">
        {(provided) => (
          <List
            dense={true}
            ref={provided.innerRef}
            {...provided.droppableProps}
          >
            {items.map((item, index) => (
              <DraggableListItem
                item={item}
                index={index}
                key={item + index}
                onRemove={onRemove}
              />
            ))}
            {provided.placeholder}
          </List>
        )}
      </Droppable>
    </DragDropContext>
  );
});

export default DraggableList;
