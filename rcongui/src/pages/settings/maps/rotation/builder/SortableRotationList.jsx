import { Box, Typography, Stack, Tooltip, IconButton } from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import SaveIcon from "@mui/icons-material/Save";
import {
  DndContext,
  PointerSensor,
  KeyboardSensor,
  useSensor,
  useSensors,
  closestCenter,
  TouchSensor,
} from "@dnd-kit/core";
import {
  SortableContext,
  verticalListSortingStrategy,
  sortableKeyboardCoordinates,
} from "@dnd-kit/sortable";
import { arrayMove } from "@dnd-kit/sortable";
import SortableRotationItem from "./SortableRotationItem";
import CopyToClipboardButton from "@/components/shared/CopyToClipboardButton";
import ReplayIcon from "@mui/icons-material/Replay";

export function SortableRotationList({
  maps,
  setMaps,
  onRemove,
  isSaving,
  onReset,
  onClear,
  onSave,
  isDisabled,
  actions,
  params,
}) {
  // Set up DnD sensors
  const sensors = useSensors(
    useSensor(PointerSensor, {
      // Require the mouse to move by 10 pixels before activating
      activationConstraint: {
        distance: 10,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    }),
    useSensor(TouchSensor),
  );

  // Handle drag end event
  const handleDragEnd = (event) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      setMaps((items) => {
        const oldIndex = items.findIndex(
          (item) => item.selectionId === active.id
        );
        const newIndex = items.findIndex(
          (item) => item.selectionId === over.id
        );

        return arrayMove(items, oldIndex, newIndex);
      });
    }
  };

  return (
    <Box
      sx={{
        border: "1px solid",
        borderColor: "divider",
        borderRadius: 1,
        height: "100%",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <Box sx={{ p: 2, borderBottom: "1px solid", borderColor: "divider" }}>
        <Stack
          direction={{ xs: "column", sm: "row" }}
          gap={1}
          alignItems={{ sx: "flex-start", md: "center" }}
          justifyContent={"space-between"}
        >
          <Typography variant="h6">Rotation ({maps.length})</Typography>
          <Stack
            direction="row"
            spacing={1}
            justifyContent={{ sx: "center", md: "flex-end" }}
          >
            {actions && (
              <>
                <Box
                  sx={{
                    flexGrow: 1,
                    display: "flex",
                    justifyContent: "flex-end",
                    gap: 1,
                  }}
                >
                  {actions}
                </Box>
                <Divider flexItem orientation="vertical" />
              </>
            )}
            <Box
              sx={{
                display: "flex",
                justifyContent: "flex-end",
                gap: 1,
              }}
            >
              <Tooltip title="Reset changes">
                <IconButton
                  variant="outlined"
                  size={"small"}
                  color="error"
                  onClick={onReset}
                >
                  <ReplayIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Clear">
                <IconButton
                  variant="outlined"
                  size={"small"}
                  color="error"
                  onClick={onClear}
                >
                  <DeleteIcon />
                </IconButton>
              </Tooltip>
              <CopyToClipboardButton
                iconOnly={true}
                title={
                  <div>
                    <div>
                      Copy the list of selected map ids to the clipboard.
                    </div>
                    <div>Useful for autosettings.</div>
                  </div>
                }
                text={JSON.stringify(
                  maps.map((item) => item.mapId || item.id),
                  null,
                  2
                )}
                size={"small"}
              />
              <Tooltip title="Save">
                <IconButton
                  variant="contained"
                  size={"small"}
                  color="primary"
                  disabled={isDisabled}
                  onClick={onSave}
                >
                  <SaveIcon />
                </IconButton>
              </Tooltip>
            </Box>
          </Stack>
        </Stack>
      </Box>

      <Box sx={{ p: 2, flexGrow: 1, overflow: "auto" }}>
        {maps.length > 0 ? (
          <DndContext
            sensors={sensors}
            collisionDetection={closestCenter}
            onDragEnd={handleDragEnd}
          >
            <SortableContext
              items={maps.map((item) => item.selectionId)}
              strategy={verticalListSortingStrategy}
            >
              {maps.map((item, index, tempRotation) => {
                console.log(tempRotation, params, index)
                let isNext = false;
                if (tempRotation.length === 1) {
                  isNext = true
                } else if (params.currentMapIndex === params.nextMapIndex) {
                  isNext = (index + 1) === params.nextMapIndex
                } else {
                  isNext = index === params.nextMapIndex
                }

                return (
                  <SortableRotationItem
                    key={item.selectionId}
                    item={item}
                    onRemove={onRemove}
                    isNext={isNext}
                  />
                )
              })}
            </SortableContext>
          </DndContext>
        ) : (
          <Box
            sx={{
              py: 5,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              color: "text.secondary",
            }}
          >
            <Box sx={{ mb: 2, opacity: 0.5 }}>
              <svg width="48" height="48" viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  d="M12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22A10,10 0 0,1 2,12A10,10 0 0,1 12,2M12,12.5A1.5,1.5 0 0,1 10.5,11A1.5,1.5 0 0,1 12,9.5A1.5,1.5 0 0,1 13.5,11A1.5,1.5 0 0,1 12,12.5M12,7.2C9.9,7.2 8.2,8.9 8.2,11C8.2,14 12,17.5 12,17.5C12,17.5 15.8,14 15.8,11C15.8,8.9 14.1,7.2 12,7.2Z"
                />
              </svg>
            </Box>
            <Typography variant="h6" gutterBottom>
              No maps in rotation
            </Typography>
            <Typography variant="body2">
              Add maps to build your rotation
            </Typography>
          </Box>
        )}
      </Box>
    </Box>
  );
}
