import { Chip, Stack, Typography } from "@mui/material";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import ConfirmButton from "@/components/shared/ConfirmButton";

const UnknownVipList = ({
  items,
  canRemove,
  busy,
  removingPlayerId,
  onRemove,
}) => {
  if (!items?.length) return null;

  return (
    <Stack spacing={1}>
      <Typography variant="subtitle2">Unknown gameserver VIPs</Typography>

      {items.map((playerId) => (
        <Stack
          key={playerId}
          direction={{ xs: "column", sm: "row" }}
          alignItems={{ xs: "stretch", sm: "center" }}
          gap={1}
        >
          <Chip
            label={playerId}
            color="warning"
            size="small"
            variant="outlined"
            sx={{ maxWidth: "100%" }}
          />

          <ConfirmButton
            buttonText={
              removingPlayerId === playerId
                ? "Removing..."
                : "Remove from gameserver"
            }
            title="Remove unknown VIP from gameserver?"
            description={
              `VIP ${playerId} will be removed directly from this ` +
              "gameserver. VIP List records and synchronization settings " +
              "will not be changed."
            }
            confirmText="Remove VIP"
            onConfirm={() => onRemove(playerId)}
            disabled={!canRemove || busy}
            buttonProps={{
              variant: "outlined",
              color: "error",
              size: "small",
              startIcon: <DeleteOutlineIcon />,
            }}
          />
        </Stack>
      ))}
    </Stack>
  );
};

export default UnknownVipList;
