import * as React from 'react';
import DraggableListItem from './DraggableListItem';
import {
  DragDropContext,
  Droppable,
  OnDragEndResponder
} from 'react-beautiful-dnd';


const DraggableList = React.memo(({ items, onDragEnd, onRemove }) => {
  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <Droppable droppableId="droppable-list">
        {provided => (
          <div ref={provided.innerRef} {...provided.droppableProps} style={{"list-style-type": "none"}}>
            {items.map((item, index) => (
              <DraggableListItem item={item} index={index} key={item + index} onRemove={onRemove}/>
            ))}
            {provided.placeholder}
          </div>
        )}
      </Droppable>
    </DragDropContext>
  );
});

export default DraggableList;
