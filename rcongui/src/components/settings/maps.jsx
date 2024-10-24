import * as React from 'react';
import {
  Collapse,
  ImageList,
  ImageListItem,
  ImageListItemBar,
  ListItemButton,
} from '@mui/material';
import {
  Form,
} from 'react-router-dom';
import dayjs from 'dayjs';
import List from '@mui/material/List';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import ExpandLess from '@mui/icons-material/ExpandLess';
import ExpandMore from '@mui/icons-material/ExpandMore';
import ArrowRightIcon from '@mui/icons-material/ArrowRight';
import { getMapImageUrl } from '../Scoreboard/utils';

export const MapHistory = ({ maps }) => {
  return (
    <ImageList
      cols={5}
      rowHeight={100}
      gap={0}
      sx={{ overflowY: 'clip', width: '100%', mb: 0 }}
      variant="quilted"
    >
      {maps.map((map, i) => {
        return (
          <ImageListItem
            key={map.start + i}
            sx={{
              '& .MuiImageListItem-img': {
                filter: `brightness(${map.isCurrent ? 0.9 : 0.3})`,
              },
              '&.MuiImageListItem-root': {
                border: (theme) =>
                  `${map.isCurrent && '1px solid ' + theme.palette.success.main}`,
              },
            }}
          >
            <img alt={map.name} src={getMapImageUrl(map.name)} />
            <ImageListItemBar
              title={map.name}
              subtitle={
                map.start
                  ? dayjs(map.start * 1000).format('dddd, MMM D HH:mm')
                  : 'In queue'
              }
              position="bottom"
            />
          </ImageListItem>
        );
      })}
    </ImageList>
  );
};

export const MapSelectionItem = ({ map, onClick }) => {
  return (
    <ListItemButton onClick={onClick} sx={{ pl: 6 }}>
      <ListItemText primary={map} />
    </ListItemButton>
  );
};

export const MapSelectionGroup = ({ name, list, onClick }) => {
  const [open, setOpen] = React.useState(false);

  const handleExpandClick = () => {
    setOpen(!open);
  };

  return (
    <>
      <ListItemButton onClick={handleExpandClick} sx={{ pl: 4 }}>
        <ListItemIcon>
          <ArrowRightIcon />
        </ListItemIcon>
        <ListItemText primary={name} />
        {open ? <ExpandLess /> : <ExpandMore />}
      </ListItemButton>
      <Collapse in={open} timeout="auto" unmountOnExit>
        <List
          component="div"
          disablePadding
          sx={{ maxHeight: 300, overflow: 'auto' }}
        >
          {list.map((map, i) => (
            <Form method="post" key={map + i}>
              <MapSelectionItem
                key={map + i}
                map={map}
                onClick={onClick({
                  action: 'map change',
                  message: `Are you sure you want to change map to ${map}?`,
                })}
              />
              <input type="hidden" name="intent" value={'change_map'} />
              <input type="hidden" name="map_name" value={map} />
            </Form>
          ))}
        </List>
      </Collapse>
    </>
  );
};

export const MapSelection = ({ open, maps, onClick }) => {
  const modes = ['Warfare', 'Offensive', 'Skirmish', 'Unknown'];

  const mapGroups = React.useMemo(
    () =>
      maps.reduce(
        (groups, map) => {
          let mode = ['warfare', 'offensive', '_off_', 'skirmish'].find(
            (mode) => map.toLowerCase().includes(mode)
          );
          if (!mode) {
            mode = 'unknown';
          }
          if (mode === '_off_') {
            mode = 'offensive';
          }
          groups[mode].push(map);
          return groups;
        },
        {
          warfare: [],
          offensive: [],
          skirmish: [],
          unknown: [],
        }
      ),
    [maps]
  );

  return (
    <Collapse in={open} timeout="auto" unmountOnExit>
      <List component="div" disablePadding>
        {modes.map(
          (name) =>
            mapGroups[name.toLowerCase()].length > 0 && (
              <MapSelectionGroup
                key={name}
                name={name}
                list={mapGroups[name.toLowerCase()]}
                onClick={onClick}
              />
            )
        )}
      </List>
    </Collapse>
  );
};
