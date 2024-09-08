import * as React from 'react';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Stack from '@mui/material/Stack';
import HomeRoundedIcon from '@mui/icons-material/HomeRounded';
import AnalyticsRoundedIcon from '@mui/icons-material/AnalyticsRounded';
import PeopleRoundedIcon from '@mui/icons-material/PeopleRounded';
import AssignmentRoundedIcon from '@mui/icons-material/AssignmentRounded';
import SettingsRoundedIcon from '@mui/icons-material/SettingsRounded';
import InfoRoundedIcon from '@mui/icons-material/InfoRounded';
import HelpRoundedIcon from '@mui/icons-material/HelpRounded';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import { navMenus } from '../Header/nav-data';
import { Link } from 'react-router-dom';
import { Collapse } from '@mui/material';

const secondaryListItems = [
  { text: 'Settings', icon: <SettingsRoundedIcon /> },
  { text: 'About', icon: <InfoRoundedIcon /> },
  { text: 'Feedback', icon: <HelpRoundedIcon /> },
];

const NavigationLink = ({ to, icon, text }) => {
  return (
    <ListItem key={to} disablePadding sx={{ display: 'block' }}>
      <ListItemButton component={Link} to={to}>
        {icon && (
          <ListItemIcon>{icon}</ListItemIcon>
        )}
        <ListItemText primary={text} />
      </ListItemButton>
    </ListItem>
  )
};

const Group = ({ groupName, icon, level = 1, children }) => {
  const [open, setOpen] = React.useState(false);

  const handleClick = () => {
    setOpen(!open);
  };

  return (
    <ListItem key={groupName} disablePadding sx={{ display: 'block' }}>
      <ListItemButton onClick={handleClick}>
        {icon && (
          <ListItemIcon>{icon}</ListItemIcon>
        )}
        <ListItemText primary={groupName} />
        {open ? <ExpandLessIcon /> : <ExpandMoreIcon />}
      </ListItemButton>
      <Collapse in={open} timeout={'auto'} unmountOnExit>
        <List
          dense
          sx={{ '& .MuiListItemButton-root': { pl: 2 * level } }}
          disablePadding
        >
          {children}
        </List>
      </Collapse>
    </ListItem>
  );
};

export default function MenuContent() {
  return (
    <Stack sx={{ flexGrow: 1, p: 1, justifyContent: 'space-between', overflow: 'hidden', }}>
      <List dense sx={{ overflowY: 'auto' }}>

        {navMenus.filter(group => !('name' in group)).map((group) => (
            group.links.map((link) => (
              <NavigationLink key={link.to} to={link.to} text={link.name} icon={link.icon} />
            ))
        ))}

        {navMenus.filter(group => 'name' in group).map((group) => (
          <Group key={group.name} groupName={group.name} icon={group.icon}>
            {group.links.map((link) => (
              <NavigationLink key={link.to} to={link.to} text={link.name} icon={link.icon} />
            ))}
          </Group>
        ))}

      </List>

      <List dense>
        {secondaryListItems.map((item, index) => (
          <ListItem key={index} disablePadding sx={{ display: 'block' }}>
            <ListItemButton disabled>
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Stack>
  );
}
