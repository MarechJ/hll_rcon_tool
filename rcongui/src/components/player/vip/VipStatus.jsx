import { Divider, Stack, Typography } from "@mui/material";
import VipEntry from "./VipEntry";

const VipStatus = ({ vip, otherVips }) => {
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

export default VipStatus;
