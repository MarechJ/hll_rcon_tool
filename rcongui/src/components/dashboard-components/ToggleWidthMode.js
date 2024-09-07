import * as React from 'react';

import WidthNormalIcon from '@mui/icons-material/WidthNormal';
import WidthFullIcon from '@mui/icons-material/WidthFull';
import MenuButton from './MenuButton';

function ToggleWidthMode({ mode, toggleWidthMode, ...props }) {
  return (
    <MenuButton
      onClick={toggleWidthMode}
      size="small"
      aria-label="button to toggle max width"
      {...props}
    >
      {mode === 'xl' ? (
        <WidthNormalIcon fontSize="small" />
      ) : (
        <WidthFullIcon fontSize="small" />
      )}
    </MenuButton>
  );
}

export default ToggleWidthMode;
