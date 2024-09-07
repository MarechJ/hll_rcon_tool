import * as React from 'react';
import Stack from '@mui/material/Stack';
import NotificationsRoundedIcon from '@mui/icons-material/NotificationsRounded';
import NavbarBreadcrumbs from './NavbarBreadcrumbs';
import MenuButton from './MenuButton';
// import CustomDatePicker from './CustomDatePicker';
// import Search from './Search';


export default function Header() {
  return (
    <Stack
      direction="row"
      sx={{
        display: { xs: 'none', lg: 'flex' },
        width: '100%',
        alignItems: { xs: 'flex-start', lg: 'center' },
        justifyContent: 'space-between',
        pt: 1.5,
      }}
      spacing={2}
    >
      <NavbarBreadcrumbs />
      <Stack direction="row" sx={{ gap: 1 }}>
        {/* <Search /> */}
        {/* <CustomDatePicker /> */}
        {/* <MenuButton showBadge aria-label="Open notifications">
          <NotificationsRoundedIcon />
        </MenuButton> */}
      </Stack>
    </Stack>
  );
}
