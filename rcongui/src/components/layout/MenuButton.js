import Badge, { badgeClasses } from '@mui/material/Badge';
import IconButton from '@mui/material/IconButton';

function MenuButton({ showBadge = false, ...props }) {
  return (
    <Badge
      color="error"
      variant="dot"
      invisible={!showBadge}
      sx={{ [`& .${badgeClasses.badge}`]: { right: 2, top: 2 } }}
    >
      <IconButton size="small" {...props} />
    </Badge>
  );
}


export default MenuButton;
