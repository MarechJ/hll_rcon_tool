import WidthNormalIcon from '@mui/icons-material/WidthNormal';
import WidthFullIcon from '@mui/icons-material/WidthFull';
import MenuButton from './MenuButton';
import { useAppStore } from "@/hooks/useAppState";

function ToggleWidthMode() {
  const widthMode = useAppStore((state) => state.widthMode);
  const toggleWidthMode = useAppStore((state) => state.toggleWidthMode);

  return (
    <MenuButton
      onClick={toggleWidthMode}
      size="small"
      aria-label="button to toggle max width"
    >
      {widthMode === 'xl' ? (
        <WidthNormalIcon fontSize="small" />
      ) : (
        <WidthFullIcon fontSize="small" />
      )}
    </MenuButton>
  );
}

export default ToggleWidthMode;
