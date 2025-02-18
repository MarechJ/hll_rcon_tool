import { Stack, Divider } from "@mui/material";
import StarIcon from "@mui/icons-material/Star";
import VisibilityIcon from "@mui/icons-material/Visibility";
import NoAccountsIcon from "@mui/icons-material/NoAccounts";
import GavelIcon from "@mui/icons-material/Gavel";
import { yellow, red } from "@mui/material/colors";

const PlayerProfileStatusTags = ({
  isVip,
  isWatched,
  isBlacklisted,
  isBanned,
}) => {
  return (
    <Stack
      direction="row"
      alignItems={"center"}
      justifyContent={"center"}
      divider={<Divider orientation="vertical" flexItem />}
      spacing={2}
      sx={{ p: 1 }}
    >
      {isVip && <StarIcon sx={{ color: yellow["500"] }} />}
      {isWatched && <VisibilityIcon />}
      {isBlacklisted && <NoAccountsIcon sx={{ color: red["500"] }} />}
      {isBanned && <GavelIcon sx={{ color: red["500"] }} />}
    </Stack>
  );
};

export default PlayerProfileStatusTags;
