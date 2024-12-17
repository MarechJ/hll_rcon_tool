import Stack from '@mui/material/Stack'
import NavbarBreadcrumbs from './NavbarBreadcrumbs'

export default function Header() {
  return (
    <Stack
      direction='row'
      sx={{
        display: { xs: 'none', lg: 'flex' },
        width: '100%',
        alignItems: { xs: 'flex-start', lg: 'center' },
        justifyContent: 'space-between',
        pt: 1.5,
        px: { xs: 0, lg: 2 }
      }}
      spacing={2}
    >
      <NavbarBreadcrumbs />
      <Stack direction='row' sx={{ gap: 1 }}></Stack>
    </Stack>
  )
}
