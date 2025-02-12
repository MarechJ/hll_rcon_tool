import { useAuth } from "@/hooks/useAuth";
import { Avatar, Box, Stack, Typography } from "@mui/material";
import OptionsMenu from "../OptionsMenu";

export const UserActions = () => {
  const { permissions } = useAuth();

  return (
    <Stack
      direction="row"
      sx={{
        p: 2,
        gap: 1,
        alignItems: "center",
        borderTop: "1px solid",
        borderColor: "divider",
      }}
    >
      <Avatar
        sizes="small"
        alt={permissions?.user_name?.toUpperCase() ?? "?"}
        sx={{ width: 36, height: 36 }}
      />
      <Box sx={{ mr: "auto" }}>
        <Typography
          variant="body2"
          sx={{ fontWeight: 500, lineHeight: "16px" }}
        >
          {permissions?.user_name ?? "?????"}
        </Typography>
      </Box>
      <OptionsMenu />
    </Stack>
  );
};
