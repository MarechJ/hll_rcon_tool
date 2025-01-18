import { usePlayerSidebar } from "@/hooks/usePlayerSidebar";
import { Box } from "@mui/material";

export const PlayerDrawerLink = ({ playerId, children, ...props }) => {
    const { openWithId } = usePlayerSidebar();
    const handleClick = () => {
      // Trigger sidebar open with player ID
      // This would need to be implemented based on your sidebar logic
      openWithId(playerId);
    };

    return (
      <Box
        component="span"
        onClick={handleClick}
        sx={{ 
          cursor: 'pointer',
          fontStyle: 'italic',
          fontWeight: 'bolder',
          "&:hover": {
            textDecoration: 'underline'
          },
          ...props.sx
        }}
      >
        {children}
      </Box>
    );
  };