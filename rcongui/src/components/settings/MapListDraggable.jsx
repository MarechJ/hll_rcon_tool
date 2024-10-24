import React, {
  createContext,
  Fragment,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';

import ReactDOM from 'react-dom';
import invariant from 'tiny-invariant';

import { triggerPostMoveFlash } from '@atlaskit/pragmatic-drag-and-drop-flourish/trigger-post-move-flash';
import {
  attachClosestEdge,
  extractClosestEdge,
} from '@atlaskit/pragmatic-drag-and-drop-hitbox/closest-edge';
import { getReorderDestinationIndex } from '@atlaskit/pragmatic-drag-and-drop-hitbox/util/get-reorder-destination-index';
import * as liveRegion from '@atlaskit/pragmatic-drag-and-drop-live-region';
import { DragHandleButton } from '@atlaskit/pragmatic-drag-and-drop-react-accessibility/drag-handle-button';
import { DropIndicator } from '@atlaskit/pragmatic-drag-and-drop-react-drop-indicator/box';
import { combine } from '@atlaskit/pragmatic-drag-and-drop/combine';
import {
  draggable,
  dropTargetForElements,
  monitorForElements,
} from '@atlaskit/pragmatic-drag-and-drop/element/adapter';
import { pointerOutsideOfPreview } from '@atlaskit/pragmatic-drag-and-drop/element/pointer-outside-of-preview';
import { setCustomNativeDragPreview } from '@atlaskit/pragmatic-drag-and-drop/element/set-custom-native-drag-preview';
import { reorder } from '@atlaskit/pragmatic-drag-and-drop/reorder';
import {
  List,
  ListItem,
  Box,
  Stack,
  Unstable_Grid2 as Grid,
  MenuList,
  MenuItem,
  Badge,
  Avatar,
  Typography,
  Menu,
  IconButton,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';

const ListContext = createContext(null);

function useListContext() {
  const listContext = useContext(ListContext);
  invariant(listContext !== null);
  return listContext;
}

const itemKey = Symbol('item');

function getItemData({ item, index, instanceId }) {
  return {
    [itemKey]: true,
    item,
    index,
    instanceId,
  };
}

function isItemData(data) {
  return data[itemKey] === true;
}

function getItemPosition({ index, items }) {
  if (items.length === 1) {
    return 'only';
  }

  if (index === 0) {
    return 'first';
  }

  if (index === items.length - 1) {
    return 'last';
  }

  return 'middle';
}

const idleState = { type: 'idle' };
const draggingState = { type: 'dragging' };

function DropDownContent({ open, anchorEl, handleClose, position, index }) {
  const { reorderItem, getListLength } = useListContext();

  const isMoveUpDisabled = position === 'first' || position === 'only';
  const isMoveDownDisabled = position === 'last' || position === 'only';

  const moveToTop = useCallback(() => {
    reorderItem({
      startIndex: index,
      indexOfTarget: 0,
      closestEdgeOfTarget: null,
    });
    handleClose();
  }, [index, reorderItem]);

  const moveUp = useCallback(() => {
    reorderItem({
      startIndex: index,
      indexOfTarget: index - 1,
      closestEdgeOfTarget: null,
    });
    handleClose();
  }, [index, reorderItem]);

  const moveDown = useCallback(() => {
    reorderItem({
      startIndex: index,
      indexOfTarget: index + 1,
      closestEdgeOfTarget: null,
    });
    handleClose();
  }, [index, reorderItem]);

  const moveToBottom = useCallback(() => {
    reorderItem({
      startIndex: index,
      indexOfTarget: getListLength() - 1,
      closestEdgeOfTarget: null,
    });
    handleClose();
  }, [index, getListLength, reorderItem]);

  return (
    <Menu anchorEl={anchorEl} open={open} onClose={handleClose}>
      <MenuItem onClick={moveToTop} disabled={isMoveUpDisabled}>Move to top</MenuItem>
      <MenuItem onClick={moveUp} disabled={isMoveUpDisabled}>Move up</MenuItem>
      <MenuItem onClick={moveDown} disabled={isMoveDownDisabled}>Move down</MenuItem>
      <MenuItem onClick={moveToBottom} disabled={isMoveDownDisabled}>Move to bottom</MenuItem>
    </Menu>
  );
}

function MapListItem({ item, index, position }) {
  const { registerItem, instanceId } = useListContext();

  const ref = useRef(null);
  const [closestEdge, setClosestEdge] = useState(null);

  const dragHandleRef = useRef(null);

  const [anchorEl, setAnchorEl] = React.useState(null);
  const open = Boolean(anchorEl);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const [draggableState, setDraggableState] = useState(idleState);

  useEffect(() => {
    const element = ref.current;
    const dragHandle = dragHandleRef.current;
    invariant(element);
    invariant(dragHandle);

    const data = getItemData({ item, index, instanceId });

    return combine(
      registerItem({ itemId: item.id, element }),
      draggable({
        element: dragHandle,
        getInitialData: () => data,
        onGenerateDragPreview({ nativeSetDragImage }) {
          setCustomNativeDragPreview({
            nativeSetDragImage,
            getOffset: pointerOutsideOfPreview({
              x: '16px',
              y: '8px',
            }),
            render({ container }) {
              setDraggableState({ type: 'preview', container });

              return () => setDraggableState(draggingState);
            },
          });
        },
        onDragStart() {
          setDraggableState(draggingState);
        },
        onDrop() {
          setDraggableState(idleState);
        },
      }),
      dropTargetForElements({
        element,
        canDrop({ source }) {
          return (
            isItemData(source.data) && source.data.instanceId === instanceId
          );
        },
        getData({ input }) {
          return attachClosestEdge(data, {
            element,
            input,
            allowedEdges: ['top', 'bottom'],
          });
        },
        onDrag({ self, source }) {
          const isSource = source.element === element;
          if (isSource) {
            setClosestEdge(null);
            return;
          }

          const closestEdge = extractClosestEdge(self.data);

          const sourceIndex = source.data.index;
          invariant(typeof sourceIndex === 'number');

          const isItemBeforeSource = index === sourceIndex - 1;
          const isItemAfterSource = index === sourceIndex + 1;

          const isDropIndicatorHidden =
            (isItemBeforeSource && closestEdge === 'bottom') ||
            (isItemAfterSource && closestEdge === 'top');

          if (isDropIndicatorHidden) {
            setClosestEdge(null);
            return;
          }

          setClosestEdge(closestEdge);
        },
        onDragLeave() {
          setClosestEdge(null);
        },
        onDrop() {
          setClosestEdge(null);
        },
      })
    );
  }, [instanceId, item, index, registerItem]);

  return (
    <ListItem
      ref={ref}
      sx={{
        py: 1,
        borderBottom: (theme) => `1px solid ${theme.palette.divider}`,
      }}
    >
      <Stack
        gap={2}
        direction={'row'}
        justifyContent={'start'}
        alignItems={'center'}
        sx={{ width: '100%' }}
      >
        <Box>
          <DragHandleButton
            ref={dragHandleRef}
            onClick={handleClick}
            label={`Reorder ${item.label}`}
            />
        </Box>
        {/* MENU */}
        <DropDownContent
          anchorEl={anchorEl}
          open={open}
          handleClose={handleClose}
          index={index}
          position={position}
        />
        <Typography
          variant="subtitle2"
          textAlign={'center'}
          sx={{ width: '3ch' }}
          component={'span'}
        >
          {index + 1}
        </Typography>
        <Avatar
          src={`/maps/${item.map.id}.webp`}
          alt={item.map.prettyname}
          size="small"
          sx={{ width: '36px', height: '36px' }}
        />
        <Box sx={{ flexGrow: 1 }}>
          <Typography
            variant="subtitle"
            component={'span'}
            sx={{ flexShrink: 1, overflow: 'hidden', textOverflow: 'ellipsis' }}
          >
            {item.map.prettyname}
          </Typography>
          <Stack direction={'row'} gap={1}>
            <Typography
              component={'span'}
              sx={{
                backgroundColor: 'grey.800',
                color: 'grey.200',
                px: 0.75,
                py: 0.25,
                fontSize: '0.7rem',
                borderRadius: 4,
              }}
            >
              {item.gamemode}
            </Typography>
            <Typography
              component={'span'}
              sx={{
                backgroundColor: 'grey.800',
                color: 'grey.200',
                px: 0.75,
                py: 0.25,
                fontSize: '0.7rem',
                borderRadius: 4,
              }}
            >
              {item.environment}
            </Typography>
          </Stack>
        </Box>
        {/* TODO */}
        {/* Pass down handleRemove */}
        <IconButton aria-label="delete">
          <DeleteIcon />
        </IconButton>
      </Stack>
      {closestEdge && <DropIndicator edge={closestEdge} gap="1px" />}
      {draggableState.type === 'preview' &&
        ReactDOM.createPortal(
          <Box
            sx={{
              paddingBlock: (theme) => theme.spacing(0.5),
              paddingInline: (theme) => theme.spacing(1),
              borderRadius: (theme) => theme.shape.borderRadius,
              backgroundColor: 'background.paper',
              maxWidth: '360px',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              display: 'flex',
              flexDirection: 'row',
              gap: 1,
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Avatar
              src={`/maps/${item.map.id}.webp`}
              alt={item.map.prettyname}
              size="small"
            />
            <Box>{item.map.prettyname}</Box>
          </Box>,
          draggableState.container
        )}
    </ListItem>
  );
}

const defaultItems = [
  {
    id: 'carentan_warfare',
    map: {
      id: 'carentan',
      name: 'CARENTAN',
      tag: 'CAR',
      prettyname: 'Carentan',
      shortname: 'Carentan',
      allies: 'us',
      axis: 'ger',
    },
    gamemode: 'warfare',
    skirmish_mode: null,
    attackers: null,
    environment: 'Day',
  },
  {
    id: 'omahabeach_warfare',
    map: {
      id: 'omaha',
      name: 'OMAHA BEACH',
      tag: 'OMA',
      prettyname: 'Omaha Beach',
      shortname: 'Omaha',
      allies: 'us',
      axis: 'ger',
    },
    gamemode: 'warfare',
    skirmish_mode: null,
    attackers: null,
    environment: 'Day',
  },

  {
    id: 'omahabeach_offensive_us',
    map: {
      id: 'omaha',
      name: 'OMAHA BEACH',
      tag: 'OMA',
      prettyname: 'Omaha Beach',
      shortname: 'Omaha',
      allies: 'us',
      axis: 'ger',
    },
    gamemode: 'offensive',
    skirmish_mode: null,
    attackers: 'allies',
    environment: 'Day',
  },

  {
    id: 'purpleheartlane_warfare',
    map: {
      id: 'phl',
      name: 'PURPLE HEART LANE',
      tag: 'PHL',
      prettyname: 'Purple Heart Lane',
      shortname: 'PHL',
      allies: 'us',
      axis: 'ger',
    },
    gamemode: 'warfare',
    skirmish_mode: null,
    attackers: null,
    environment: 'Day',
  },

  {
    id: 'purpleheartlane_offensive_us',
    map: {
      id: 'phl',
      name: 'PURPLE HEART LANE',
      tag: 'PHL',
      prettyname: 'Purple Heart Lane',
      shortname: 'PHL',
      allies: 'us',
      axis: 'ger',
    },
    gamemode: 'offensive',
    skirmish_mode: null,
    attackers: 'allies',
    environment: 'Day',
  },

  {
    id: 'hurtgenforest_warfare',
    map: {
      id: 'hurtgen',
      name: 'HÜRTGEN FOREST',
      tag: 'HUR',
      prettyname: 'Hurtgen Forest',
      shortname: 'Hurtgen',
      allies: 'us',
      axis: 'ger',
    },
    gamemode: 'warfare',
    skirmish_mode: null,
    attackers: null,
    environment: 'Day',
  },

  {
    id: 'hurtgenforest_offensive_ger',
    map: {
      id: 'hurtgen',
      name: 'HÜRTGEN FOREST',
      tag: 'HUR',
      prettyname: 'Hurtgen Forest',
      shortname: 'Hurtgen',
      allies: 'us',
      axis: 'ger',
    },
    gamemode: 'offensive',
    skirmish_mode: null,
    attackers: 'axis',
    environment: 'Day',
  },

  {
    id: 'hill400_warfare',
    map: {
      id: 'hill400',
      name: 'HILL 400',
      tag: 'HIL',
      prettyname: 'Hill 400',
      shortname: 'Hill 400',
      allies: 'us',
      axis: 'ger',
    },
    gamemode: 'warfare',
    skirmish_mode: null,
    attackers: null,
    environment: 'Day',
  },

  {
    id: 'hill400_offensive_us',
    map: {
      id: 'hill400',
      name: 'HILL 400',
      tag: 'HIL',
      prettyname: 'Hill 400',
      shortname: 'Hill 400',
      allies: 'us',
      axis: 'ger',
    },
    gamemode: 'offensive',
    skirmish_mode: null,
    attackers: 'allies',
    environment: 'Day',
  },

  {
    id: 'foy_warfare',
    map: {
      id: 'foy',
      name: 'FOY',
      tag: 'FOY',
      prettyname: 'Foy',
      shortname: 'Foy',
      allies: 'us',
      axis: 'ger',
    },
    gamemode: 'warfare',
    skirmish_mode: null,
    attackers: null,
    environment: 'Day',
  },

  {
    id: 'foy_offensive_ger',
    map: {
      id: 'foy',
      name: 'FOY',
      tag: 'FOY',
      prettyname: 'Foy',
      shortname: 'Foy',
      allies: 'us',
      axis: 'ger',
    },
    gamemode: 'offensive',
    skirmish_mode: null,
    attackers: 'axis',
    environment: 'Day',
  },
];

function getItemRegistry() {
  const registry = new Map();

  function register({ itemId, element }) {
    registry.set(itemId, element);

    return function unregister() {
      registry.delete(itemId);
    };
  }

  function getElement(itemId) {
    return registry.get(itemId) ?? null;
  }

  return { register, getElement };
}

export default function MapRotationDrag() {
  const [{ items, lastCardMoved }, setListState] = useState({
    items: defaultItems,
    lastCardMoved: null,
  });
  const [registry] = useState(getItemRegistry);

  // Isolated instances of this component from one another
  const [instanceId] = useState(() => Symbol('instance-id'));

  const reorderItem = useCallback(
    ({ startIndex, indexOfTarget, closestEdgeOfTarget }) => {
      const finishIndex = getReorderDestinationIndex({
        startIndex,
        closestEdgeOfTarget,
        indexOfTarget,
        axis: 'vertical',
      });

      if (finishIndex === startIndex) {
        // If there would be no change, we skip the update
        return;
      }

      setListState((listState) => {
        const item = listState.items[startIndex];

        return {
          items: reorder({
            list: listState.items,
            startIndex,
            finishIndex,
          }),
          lastCardMoved: {
            item,
            previousIndex: startIndex,
            currentIndex: finishIndex,
            numberOfItems: listState.items.length,
          },
        };
      });
    },
    []
  );

  useEffect(() => {
    return monitorForElements({
      canMonitor({ source }) {
        return isItemData(source.data) && source.data.instanceId === instanceId;
      },
      onDrop({ location, source }) {
        const target = location.current.dropTargets[0];
        if (!target) {
          return;
        }

        const sourceData = source.data;
        const targetData = target.data;
        if (!isItemData(sourceData) || !isItemData(targetData)) {
          return;
        }

        const indexOfTarget = items.findIndex(
          (item) => item.id === targetData.item.id
        );
        if (indexOfTarget < 0) {
          return;
        }

        const closestEdgeOfTarget = extractClosestEdge(targetData);

        reorderItem({
          startIndex: sourceData.index,
          indexOfTarget,
          closestEdgeOfTarget,
        });
      },
    });
  }, [instanceId, items, reorderItem]);

  // once a drag is finished, we have some post drop actions to take
  useEffect(() => {
    if (lastCardMoved === null) {
      return;
    }

    const { item, previousIndex, currentIndex, numberOfItems } = lastCardMoved;
    const element = registry.getElement(item.id);
    if (element) {
      triggerPostMoveFlash(element);
    }

    liveRegion.announce(
      `You've moved ${item.label} from position ${
        previousIndex + 1
      } to position ${currentIndex + 1} of ${numberOfItems}.`
    );
  }, [lastCardMoved, registry]);

  // cleanup the live region when this component is finished
  useEffect(() => {
    return function cleanup() {
      liveRegion.cleanup();
    };
  }, []);

  const getListLength = useCallback(() => items.length, [items.length]);

  const contextValue = useMemo(() => {
    return {
      registerItem: registry.register,
      reorderItem,
      instanceId,
      getListLength,
    };
  }, [registry.register, reorderItem, instanceId, getListLength]);

  return (
    <ListContext.Provider value={contextValue}>
      <List>
        {/*
            It is not expensive for us to pass `index` to items for this example,
            as when reordering, only two items index will ever change.
  
            If insertion or removal where allowed, it would be worth making
            `index` a getter (eg `getIndex()`) to avoid re-rendering many items
          */}
        {items.map((item, index) => (
          <MapListItem
            key={item.id}
            item={item}
            index={index}
            position={getItemPosition({ index, items })}
          />
        ))}
      </List>
    </ListContext.Provider>
  );
}
