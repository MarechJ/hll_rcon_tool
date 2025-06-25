import { Box, IconButton, Tooltip } from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { MapDetailsCard } from "../../MapDetailsCard";

function SortableRotationItem({ item, onRemove }) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({
    id: item.selectionId,
  });

  const mapLayer = item;

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    zIndex: isDragging ? 10 : 1,
    opacity: isDragging ? 0.8 : 1,
  };

  return (
    <Box
      ref={setNodeRef}
      style={style}
      sx={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        p: 0.5,
        mb: 1,
        borderRadius: 1,
        border: "1px solid",
        borderColor: "divider",
        boxShadow: isDragging ? 3 : 1,
      }}
    >
      <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
        <Box
          {...attributes}
          {...listeners}
          sx={{
            cursor: "grab",
            "&:active": { cursor: "grabbing" },
            p: 1,
            borderRadius: 1,
            "&:hover": { bgcolor: "action.hover" },
          }}
        >
          <svg width="24" height="24" viewBox="0 0 24 24">
            <path
              fill="currentColor"
              d="M7,19V17H9V19H7M11,19V17H13V19H11M15,19V17H17V19H15M7,15V13H9V15H7M11,15V13H13V15H11M15,15V13H17V15H15M7,11V9H9V11H7M11,11V9H13V11H11M15,11V9H17V11H15M7,7V5H9V7H7M11,7V5H13V7H11M15,7V5H17V7H15Z"
            />
          </svg>
        </Box>
        <MapDetailsCard mapLayer={mapLayer} />
      </Box>
      <Box sx={{ display: "flex", gap: 1 }}>
        <Tooltip title="Remove from rotation">
          <IconButton size="small" onClick={() => onRemove(mapLayer)} color="error">
            <CloseIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>
    </Box>
  );
}

export default SortableRotationItem;
