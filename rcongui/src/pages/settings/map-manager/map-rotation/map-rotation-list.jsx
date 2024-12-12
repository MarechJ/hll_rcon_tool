import {makeStyles} from "@mui/styles";
import {IconButton, ListItem, ListItemAvatar, ListItemText, Stack, Tooltip,} from "@mui/material";
import Avatar from "@mui/material/Avatar";
import DeleteIcon from "@mui/icons-material/Delete";
import InputIcon from "@mui/icons-material/Input";
import {MapDescription} from "@/components/MapManager/map-details";
import {getMapLayerImageSrc} from "@/components/MapManager/helpers";
import {memo, useEffect, useState} from "react";
import {
  closestCenter,
  DndContext,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy
} from "@dnd-kit/sortable";
import {restrictToVerticalAxis} from "@dnd-kit/modifiers";
import {CSS} from "@dnd-kit/utilities";

const useStyles = makeStyles((theme) => ({
  draggingListItem: {
    boxShadow: "rgba(6, 24, 44, 0.4) 0px 0px 0px 2px, rgba(6, 24, 44, 0.65) 0px 4px 6px -1px, rgba(255, 255, 255, 0.08) 0px 1px 0px 0px inset",
  }, base: {
    borderBottom: `1px solid ${theme.palette.divider}`,
  }, secondaryAction: {
    display: "flex", flexDirection: "row", gap: theme.spacing(2),
  },
}));

function Sortable({thisList, mapLayer, index, id, onRemove, onChange, isSaved}) {
  const {
    attributes, listeners, setNodeRef, isDragging, transform, transition
  } = useSortable({id: id});

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (<div ref={setNodeRef} {...listeners} {...attributes} style={style}>
    <Item
      key={id}
      index={index}
      thisList={thisList}
      mapLayer={mapLayer}
      onRemove={onRemove}
      onChange={onChange}
      isSaved={isSaved}
      isDragging={isDragging}
    />
  </div>);
}

const Item = ({thisList, isDragging, mapLayer, index, onRemove, onChange, isSaved}) => {
  const classes = useStyles();

  return <ListItem
    className={isDragging ? classes.draggingListItem : classes.base}
    secondaryAction={<Stack direction="row" gap={2}>
      {thisList.findIndex((aMapLayer) => aMapLayer.id === mapLayer.id) === index && (<Tooltip title={"Change map"}>
        <span>
          <IconButton
            edge="end"
            aria-label="set map"
            disabled={!isSaved}
            onClick={() => onChange(mapLayer)}
            size="large"
          >
            <InputIcon/>
          </IconButton>
        </span>
      </Tooltip>)}
      <IconButton
        edge="end"
        aria-label="delete"
        onClick={() => onRemove(index)}
        size="large"
      >
        <DeleteIcon/>
      </IconButton>
    </Stack>}
  >
    <ListItemAvatar>
      <Avatar src={getMapLayerImageSrc(mapLayer)}/>
    </ListItemAvatar>
    <ListItemText
      primary={mapLayer.map.pretty_name}
      secondary={<MapDescription mapLayer={mapLayer}/>}
    />
  </ListItem>
}

const DraggableList = memo(({maps, onDragEnd, onRemove, onChange, isSaved}) => {
  function handleDragEnd(event) {
    const {active, over} = event;

    if (active.id !== over.id) {
      const oldIndex = items.findIndex((m) => m.id === active.id);
      const newIndex = items.findIndex((m) => m.id === over.id);

      // for visual smoothyness only: change the items in our state before
      // it is passed in as a new maps array
      setItems((it) => {
        return arrayMove(it, oldIndex, newIndex);
      });
      onDragEnd({
        destination: {index: newIndex}, source: {index: oldIndex},
      });
    }
  }

  useEffect(() => {
    setItems(maps.map((m, idx) => ({...m, id: `${m.id}-${idx}`})));
  }, [maps]);

  const [items, setItems] = useState([]);
  const sensors = useSensors(useSensor(PointerSensor), useSensor(KeyboardSensor, {
    coordinateGetter: sortableKeyboardCoordinates,
  }));

  return <DndContext
    sensors={sensors}
    collisionDetection={closestCenter}
    modifiers={[restrictToVerticalAxis]}
    onDragEnd={handleDragEnd}
  >
    <SortableContext
      items={items}
      strategy={verticalListSortingStrategy}
    >
      {items.map((mapLayer, index, thisList) => (<Sortable
        id={mapLayer.id}
        key={mapLayer.id}
        index={index}
        thisList={thisList}
        mapLayer={mapLayer}
        onRemove={onRemove}
        onChange={onChange}
        isSaved={isSaved}
      />))}
    </SortableContext>
  </DndContext>
});

export default DraggableList;
