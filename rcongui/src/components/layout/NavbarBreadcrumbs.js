import { styled } from '@mui/material/styles';
import Typography from '@mui/material/Typography';
import Breadcrumbs, { breadcrumbsClasses } from '@mui/material/Breadcrumbs';
import NavigateNextRoundedIcon from '@mui/icons-material/NavigateNextRounded';
import { Link, useLocation } from 'react-router-dom';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import ListItemIcon from '@mui/material/ListItemIcon';
import { Fragment, useState } from 'react';
import Popper from '@mui/material/Popper';
import ClickAwayListener from '@mui/material/ClickAwayListener';
import Box from '@mui/material/Box';
import { navMenus } from '@/components/Header/nav-data';

const StyledBreadcrumbs = styled(Breadcrumbs)(({ theme }) => ({
  margin: theme.spacing(1, 0),
  [`& .${breadcrumbsClasses.separator}`]: {
    color: theme.palette.action.disabled,
    margin: 1,
  },
  [`& .${breadcrumbsClasses.ol}`]: {
    alignItems: 'center',
  },
}));

const StyledPopper = styled(Popper)(({ theme }) => ({
  border: `1px solid ${theme.palette.divider}`,
  boxShadow: theme.shadows[4],
  backgroundColor: theme.palette.background.paper,
  borderRadius: theme.shape.borderRadius,
  width: 'fit-content',
  zIndex: theme.zIndex.modal,
}));

// BreadcrumbPopover component
const BreadcrumbPopover = ({ text, menu, children, renderButton }) => {
  const [anchorEl, setAnchorEl] = useState(null);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const open = Boolean(anchorEl);
  const id = open ? `breadcrumb-menu-${text}` : undefined;

  return (
    <Fragment>
      {renderButton({ onClick: handleClick })}
      <StyledPopper
        id={id}
        open={open}
        anchorEl={anchorEl}
        placement="bottom-start"
        sx={{ width: 'fit-content' }}
      >
        <ClickAwayListener onClickAway={handleClose}>
          <Box>
            <Box
              sx={{
                borderBottom: (theme) => `1px solid ${theme.palette.divider}`,
                padding: 1,
                fontWeight: 600,
              }}
            >
              Navigate to
            </Box>
            <List>
              {menu.links.map((item) => (
                <ListItem key={item.to} disablePadding>
                  <ListItemButton 
                    component={Link} 
                    to={item.to}
                    onClick={handleClose}
                  >
                    {item.icon && (
                      <ListItemIcon sx={{ minWidth: 40 }}>
                        {item.icon}
                      </ListItemIcon>
                    )}
                    <ListItemText primary={item.name} />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
          </Box>
        </ClickAwayListener>
      </StyledPopper>
    </Fragment>
  );
};

// Helper function to find menu and its children
const findMenuByName = (name) => {
  return navMenus.find(menu => 
    menu.name?.toLowerCase() === name?.toLowerCase()
  );
};

// Helper function to find menu item's path
const findMenuItemPath = (name) => {
  for (const menu of navMenus) {
    // Check if it's a top-level menu with a direct link
    if (menu.name?.toLowerCase() === name?.toLowerCase() && menu.links?.[0]?.to) {
      return menu.links[0].to;
    }
    // Check menu items
    const link = menu.links?.find(link => 
      link.name.toLowerCase() === name?.toLowerCase()
    );
    if (link) {
      return link.to;
    }
  }
  return '/';
};

const BreadcrumbItem = ({ text, isParent, isLast }) => {
  const menu = findMenuByName(text);
  const path = findMenuItemPath(text);
  const hasChildren = menu?.links?.length > 1; // Only consider it has children if there's more than one link

  // If it's the last item or doesn't have children, render as a link (except for the last item if it's an ID)
  if (isLast || !hasChildren) {
    const isId = text.length > 16; // Simple check for ID-like text
    if (isLast && isId) {
      return (
        <Typography 
          variant="body1" 
          sx={{ color: 'text.primary', fontWeight: 600 }}
        >
          {text}
        </Typography>
      );
    }
    return (
      <Typography
        component={Link}
        to={path}
        variant="body1"
        sx={(theme) => ({
          color: isLast ? 'text.primary' : 'inherit',
          fontWeight: isLast ? 600 : 400,
          textDecoration: 'none',
          '&:hover': {
            color: theme.palette.primary.main,
          }
        })}
      >
        {text}
      </Typography>
    );
  }

  // If it has children, render as popover menu
  return (
    <BreadcrumbPopover
      text={text}
      menu={menu}
      renderButton={(props) => (
        <Typography
          {...props}
          variant="body1"
          sx={(theme) => ({
            cursor: 'pointer',
            '&:hover': {
              color: theme.palette.primary.main,
            }
          })}
        >
          {text}
        </Typography>
      )}
    />
  );
};

export default function NavbarBreadcrumbs() {
  const location = useLocation();
  const pathSegments = location.pathname.split('/').filter(Boolean);
  
  // Build breadcrumbs based on path segments
  const breadcrumbs = pathSegments.map((segment, index) => {
    // Convert path segment to title case for display
    const text = segment.charAt(0).toUpperCase() + segment.slice(1);
    const isParent = index < pathSegments.length - 1;
    const isLast = index === pathSegments.length - 1;
    
    return { text, isParent, isLast };
  });

  return (
    <StyledBreadcrumbs
      aria-label="breadcrumb"
      separator={<NavigateNextRoundedIcon fontSize="small" />}
    >
      {/* Home breadcrumb */}
      <BreadcrumbItem 
        text="Home"
        isParent={false}
        isLast={breadcrumbs.length === 0}
      />
      
      {/* Path-based breadcrumbs */}
      {breadcrumbs.map((item, index) => (
        <BreadcrumbItem 
          key={index}
          {...item}
        />
      ))}
    </StyledBreadcrumbs>
  );
}
