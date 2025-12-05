import { generatePlayerActions } from "@/features/player-action/actions";
import {
  Card,
  CardContent,
  Stack,
  Divider,
  Typography,
  Tooltip,
  CardActions,
  IconButton,
  Box,
} from "@mui/material";
import StarIcon from "@mui/icons-material/Star";
import VisibilityIcon from "@mui/icons-material/Visibility";
import NoAccountsIcon from "@mui/icons-material/NoAccounts";
import GavelIcon from "@mui/icons-material/Gavel";
import dayjs from "dayjs";
import Emoji from "@/components/shared/Emoji";
import PlayerProfileHeader from "@/components/player/profile/Header";
import { red, yellow } from "@mui/material/colors";

export default function PlayerCard({ player }) {
  const actionList = generatePlayerActions({
    multiAction: false,
    onlineAction: player.is_online,
  });

  const name = player?.account?.name ?? player.names?.[0]?.name ?? player?.soldier?.name ?? "???";
  const avatar = player?.steaminfo?.profile?.avatar ?? name;
  const flags = player?.flags;
  const isWatched = player?.watchlist && player?.watchlist?.is_watched;
  const isBlacklisted = player?.is_blacklisted;
  const isBanned = player?.is_banned;
  const isVip = player.is_vip;
  const penalties = player?.penalty_count;
  const firstSeen = dayjs(player.first_seen_timestamp_ms).format(
    "MMM DD, YYYY"
  );
  const lastSeen = dayjs(player.last_seen_timestamp_ms).fromNow();
  const country =
    player?.country ?? player?.account?.country ?? player?.steaminfo?.country;
  const totalPlaytime = dayjs
    .duration(player.total_playtime_seconds * 1000)
    .asHours()
    .toFixed(1);
  const level = player?.level ?? player?.soldier?.level;
  const platform = player?.platform ?? player?.soldier?.platform;
  const clanTag = player?.clan_tag ?? player?.soldier?.clan_tag;

  return (
    <Card>
      <CardContent>
        <PlayerProfileHeader
          player={player}
          isOnline={player.is_online}
          actionList={actionList}
          avatar={avatar}
          name={name}
          level={level}
          country={country}
          platform={platform}
          clanTag={clanTag}
        />
        <Stack
          direction={"row"}
          spacing={1}
          sx={{
            justifyContent: "start",
            height: 30,
            alignItems: "center",
            pt: 1,
            px: 1,
          }}
        >
          {flags?.map(({ flag, comment, modified }) => (
            <Tooltip title={comment} key={flag}>
              <span>
                <Emoji emoji={flag} size={16} />
              </span>
            </Tooltip>
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
      </CardContent>
      <CardActions disableSpacing>
        <IconButton aria-label="add to favorites">
          <StarIcon
            sx={{
              fontSize: 18,
              opacity: !isVip ? 0.35 : 1,
              color: isVip && yellow["700"],
            }}
          />
        </IconButton>
        <IconButton aria-label="share">
          <VisibilityIcon
            sx={{ fontSize: 18, opacity: !isWatched ? 0.35 : 1 }}
          />
        </IconButton>
        <IconButton aria-label="share">
          <NoAccountsIcon
            sx={{
              fontSize: 18,
              opacity: !isBlacklisted ? 0.35 : 1,
              color: isBlacklisted && red["500"],
            }}
          />
        </IconButton>
        <IconButton aria-label="share">
          <GavelIcon
            sx={{
              fontSize: 18,
              opacity: !isBanned ? 0.35 : 1,
              color: isBanned && red["500"],
            }}
          />
        </IconButton>
        <Box sx={{ flexGrow: 1 }} />
      </CardActions>
    </Card>
  );
}
