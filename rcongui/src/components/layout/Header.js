import { Box, Stack } from "@mui/material";
import NavbarBreadcrumbs from "./NavbarBreadcrumbs";
import ToggleWidthMode from "./ToggleWidthMode";
import ToggleColorMode from "./ColorModeIconDropdown";
import ColorSchemeSelector from "./ColorSchemeSelector";
import MenuButton from "./MenuButton";
import MenuRoundedIcon from "@mui/icons-material/MenuRounded";
import MenuOpenIcon from "@mui/icons-material/MenuOpen";
import { useAppStore } from "@/stores/app-state";

export default function Header() {
  const openDrawer = useAppStore((state) => state.openDrawer);
  const toggleDrawer = useAppStore((state) => state.toggleDrawer);

  return (
    <Stack
      direction="row"
      sx={{
        display: { xs: "none", lg: "flex" },
        width: "100%",
        alignItems: { xs: "flex-start", lg: "center" },
        justifyContent: "space-between",
        pt: 1.5,
        px: { xs: 0, lg: 2 },
      }}
      spacing={2}
    >
      <Stack direction="row" sx={{ gap: 1 }}>
        <MenuButton
          aria-label="toggle-menu"
          onClick={toggleDrawer}
          sx={{ display: { xs: "none", lg: "inline-flex" } }}
        >
          {!openDrawer ? <MenuRoundedIcon /> : <MenuOpenIcon />}
        </MenuButton>
        <NavbarBreadcrumbs />
      </Stack>
      <Stack direction="row" sx={{ gap: 1 }}>
        <Box sx={{ display: "flex", gap: 2, width: "fit-content" }}>
          <ToggleWidthMode />
          <ColorSchemeSelector />
          <ToggleColorMode />
        </Box>
      </Stack>
    </Stack>
  );
}