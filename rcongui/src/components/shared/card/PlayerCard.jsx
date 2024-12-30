import { ActionMenuButton } from "@/features/player-action/ActionMenu";
import { generatePlayerActions } from "@/features/player-action/actions";
import {
  Card,
  CardHeader,
  CardContent,
  Avatar,
  Stack,
  Divider,
  Typography,
  Box,
} from "@mui/material";
import StarIcon from "@mui/icons-material/Star";
import VisibilityIcon from "@mui/icons-material/Visibility";
import NoAccountsIcon from "@mui/icons-material/NoAccounts";
import GavelIcon from "@mui/icons-material/Gavel";
import dayjs from "dayjs";
import Emoji from "@/components/shared/Emoji";
import CopyableText from "../CopyableText";
import { usePlayerSidebar } from "@/hooks/usePlayerSidebar";

export default function PlayerCard({ player }) {
  const { openWithId } = usePlayerSidebar();

  const name = player.names.length > 0 ? player.names[0].name : "???";
  const avatar = player?.steaminfo?.profile?.avatar ?? name;
  const flags = player?.flags;
  const isWatched = player?.watchlist && player?.watchlist?.is_watched;
  const isBlacklisted = player?.is_blacklisted;
  const isBanned = player?.is_banned;
  const isVip = player.is_vip;
  const penalties = player?.penalty_count;
  const firstSeen = dayjs(player.first_seen_timestamp_ms).format("MMM DD, YYYY");
  const lastSeen = dayjs(player.last_seen_timestamp_ms).fromNow();
  const totalPlaytime = dayjs
    .duration(player.total_playtime_seconds * 1000)
    .asHours()
    .toFixed(1);

  return (
    <Card sx={{ height: "100%", width: "100%" }}>
      <CardHeader
        avatar={<Avatar src={avatar}>{name.charAt(0)}</Avatar>}
        title={
          <Box
            component="button"
            onClick={() => openWithId(player.player_id)}
            sx={{
              textTransform: "none",
              fontSize: "1rem",
              border: "none",
              padding: 0,
              background: "none",
              cursor: "pointer",
              color: "text.primary",
              fontWeight: 500,
              "&:hover": {
                textDecoration: "underline",
                color: "text.primary",
                background: "none",
              },
            }}
          >
            {name}
          </Box>
        }
        subheader={<CopyableText text={player.player_id} />}
        subheaderTypographyProps={{
          fontSize: "0.7rem",
        }}
        titleTypographyProps={{
          fontSize: 18,
        }}
        action={
          <ActionMenuButton
            withProfile
            recipients={{
              player_id: player.player_id,
              name,
            }}
            actions={generatePlayerActions()}
          />
        }
      />
      <CardContent>
        <Stack
          direction="row"
          alignItems={"center"}
          justifyContent={"center"}
          spacing={1}
          sx={{ pt: 1, height: 30 }}
        >
          {flags?.map(({ flag }) => (
            <Typography key={flag} variant="body" color="text.secondary">
              <Emoji emoji={flag} size={18} />
            </Typography>
          ))}
        </Stack>
        <Stack
          direction="row"
          alignItems={"center"}
          justifyContent={"space-between"}
          spacing={2}
          sx={{ p: 1 }}
        >
          <div>
            <Typography variant="body2" color="text.secondary">
              Created
            </Typography>
            <Typography
              variant="caption"
              fontWeight={500}
              color="text.secondary"
            >
              {firstSeen}
            </Typography>
          </div>
          <div>
            <Typography variant="body2" color="text.secondary">
              Total Playtime
            </Typography>
            <Typography
              variant="caption"
              fontWeight={500}
              color="text.secondary"
            >
              {totalPlaytime} hours
            </Typography>
          </div>
          <div>
            <Typography variant="body2" color="text.secondary">
              Last Seen
            </Typography>
            <Typography
              variant="caption"
              fontWeight={500}
              color="text.secondary"
            >
              {lastSeen}
            </Typography>
          </div>
        </Stack>
        <Divider sx={{ my: 0 }} />
        <Stack
          direction="row"
          alignItems={"center"}
          justifyContent={"space-between"}
          spacing={2}
          sx={{ p: 1 }}
        >
          <Typography variant="caption" color="text.secondary">
            PUNISH:{" "}
            <Typography variant="caption" color="text.primary">
              {penalties?.PUNISH ?? 0}
            </Typography>
          </Typography>
          <Typography variant="caption" color="text.secondary">
            KICK:{" "}
            <Typography variant="caption" color="text.primary">
              {penalties?.KICK ?? 0}
            </Typography>
          </Typography>
          <Typography variant="caption" color="text.secondary">
            TEMPBAN:{" "}
            <Typography variant="caption" color="text.primary">
              {penalties?.TEMPBAN ?? 0}
            </Typography>
          </Typography>
          <Typography variant="caption" color="text.secondary">
            PERMABAN:{" "}
            <Typography variant="caption" color="text.primary">
              {penalties?.PERMABAN ?? 0}
            </Typography>
          </Typography>
        </Stack>
        <Stack
          direction="row"
          alignItems={"center"}
          justifyContent={"center"}
          divider={<Divider orientation="vertical" flexItem />}
          spacing={2}
          sx={{ p: 1 }}
        >
          {<StarIcon sx={{ fontSize: 24, opacity: !isVip ? 0.1 : 1 }} />}
          {
            <VisibilityIcon
              sx={{ fontSize: 24, opacity: !isWatched ? 0.1 : 1 }}
            />
          }
          {
            <NoAccountsIcon
              sx={{ fontSize: 24, opacity: !isBlacklisted ? 0.1 : 1 }}
            />
          }
          {<GavelIcon sx={{ fontSize: 24, opacity: !isBanned ? 0.1 : 1 }} />}
        </Stack>
      </CardContent>
    </Card>
  );
}
