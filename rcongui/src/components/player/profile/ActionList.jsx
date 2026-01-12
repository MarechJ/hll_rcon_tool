import { ActionIconButton } from "@/features/player-action/ActionMenu";
import { Actions } from "@/features/player-action/actions";
import { Stack } from "@mui/material";
import { red, yellow } from "@mui/material/colors";

function ActionList({ playerProfile }) {
  const isWatched = playerProfile.is_watched;
  const isBlacklisted = playerProfile.is_blacklisted;
  const isBanned = playerProfile.is_banned;
  const isVip = playerProfile.is_vip;
  return (
    <Stack direction="row" spacing={0.5}>
      <ActionIconButton
        action={!isVip ? Actions.AddVIP : Actions.RemoveVIP}
        recipients={[playerProfile]}
        sx={{
          opacity: !isVip ? 0.35 : 1,
          color: isVip && yellow["700"],
          fontSize: "1.25rem",
        }}
      />
      <ActionIconButton
        action={!isWatched ? Actions.AddWatch : Actions.RemoveWatch}
        recipients={[playerProfile]}
        sx={{ opacity: !isWatched ? 0.35 : 1, fontSize: "1.25rem" }}
      />
      <ActionIconButton
        action={Actions.AddBlacklist}
        recipients={[playerProfile]}
        sx={{
          opacity: !isBlacklisted ? 0.35 : 1,
          color: isBlacklisted && red["500"],
          fontSize: "1.25rem",
        }}
      />
      <ActionIconButton
        action={!isBanned ? Actions.TempBan : Actions.RemoveBan}
        recipients={[playerProfile]}
        sx={{
          opacity: !isBanned ? 0.35 : 1,
          color: isBanned && red["500"],
          fontSize: "1.25rem",
        }}
      />
    </Stack>
  );
}

export default ActionList;
