import { Stack, Typography, Chip, Divider } from "@mui/material";
import dayjs from "dayjs";
import WarningIcon from "@mui/icons-material/Warning";

const VipList = ({ vip, otherVips }) => {
  if (!vip && otherVips.length === 0) {
    return <Typography>No VIP records found</Typography>;
  }

  return (
    <Stack spacing={1}>
      {otherVips.map((vip_record) => (
        <VipEntry key={vip_record.id} vip={vip_record} />
      ))}
    </Stack>
  );
};

const VipEntry = ({ vip }) => {
  // vip.expiration is null if the VIP expiration is set indefinitely
  const expiresAt = dayjs(vip.expires_at);
  const isActive = vip.is_active;
  // When the VIP is not created by CRCON, there is player.vip = true but no vip record entry exists
  const isNotCreatedByCrcon = vip.not_created_by_crcon;

  console.log(`${JSON.stringify(vip)}`);

  return (
    <Stack direction="row" alignItems="center" spacing={1}>
      <Typography variant="body2" component="span">
        Server #{vip.vip_list.servers ? vip.vip_list.servers : "All"}
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
        {isActive && expiresAt
          ? "until " + dayjs(vip.expiresAt).format("LLL")
          : ""}{" "}
        {}
      </Typography>
    </Stack>
  );
};

export default VipList;
