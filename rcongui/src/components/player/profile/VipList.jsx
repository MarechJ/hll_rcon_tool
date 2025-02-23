import { Stack, Typography, Chip, Divider } from "@mui/material";
import dayjs from "dayjs";
import WarningIcon from "@mui/icons-material/Warning";

const VipList = ({ vip, otherVips }) => {
  if (!vip && otherVips.length === 0) {
    return <Typography>No VIP records found</Typography>;
  }

  return (
    <Stack spacing={1}>
      {vip && <VipEntry vip={vip} />}
      {otherVips.length > 0 && (
        <>
          {vip && <Divider variant="middle" sx={{ my: 4 }} />}
          {otherVips.map((vip) => (
            <VipEntry key={vip.server_number} vip={vip} />
          ))}
        </>
      )}
    </Stack>
  );
};

const VipEntry = ({ vip }) => {
  // vip.expiration is null if the VIP expiration is set indefinitely
  const expiration = dayjs(vip.expiration);
  const isActive = expiration === null ? true : expiration.isAfter(dayjs());
  // When the VIP is not created by CRCON, there is player.vip = true but no vip record entry exists
  const isNotCreatedByCrcon = vip.not_created_by_crcon;

  return (
    <Stack direction="row" alignItems="center" spacing={1}>
      <Typography variant="body2" component="span">
        Server #{vip.server_number}
      </Typography>
      <div>
        <Chip
          label={isActive ? "VIP" : "Expired"}
          color={isActive ? "primary" : "error"}
          variant={isActive ? "filled" : "outlined"}
          icon={isNotCreatedByCrcon ? <WarningIcon /> : null}
        />
      </div>
      <Typography variant="body2" component="span">
        {isActive ? "until" : "from"} {dayjs(vip.expiration).format("LLL")}
      </Typography>
    </Stack>
  );
};

export default VipList;
