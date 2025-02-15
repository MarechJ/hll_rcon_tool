import { Chip, Stack, Typography } from "@mui/material";
import dayjs from "dayjs";
import WarningIcon from "@mui/icons-material/Warning";

const VipEntry = ({ vip }) => {
  console.log(vip);
  // vip.expiration is null if the VIP expiration is set indefinitely
  const expiration = dayjs(vip.expiration);
  const isActive = expiration === null ? true : expiration.isAfter(dayjs());
  // When the VIP is not created by CRCON, there is player.vip = true but no vip record entry exists
  const isNotCreatedByCrcon = vip.not_created_by_crcon;

  return (
    <Chip
      label={
        isActive
          ? `Server #${vip.server_number} till ${dayjs(
              vip.expiration
            ).format("LLL")}`
          : `Server #${vip.server_number} expired on ${dayjs(
              vip.expiration
            ).format("LLL")}`
      }
      color={isActive ? "primary" : "error"}
      variant={isActive ? "filled" : "outlined"}
      icon={isNotCreatedByCrcon ? <WarningIcon /> : null}
    />
  );
};

export default VipEntry;
