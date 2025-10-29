import { OnlineStatusBadge, ProfileHeader } from "./styled";
import { Avatar, Box, Typography, Stack } from "@mui/material";
import { Link } from "react-router-dom";
import CopyableText from "@/components/shared/CopyableText";
import { ActionMenuButton } from "@/features/player-action/ActionMenu";
import PlatformChip from "./Platform";
import CountryChip from "./Country";
import LevelChip from "./Level";

const PlayerProfileHeader = ({
  player,
  isOnline,
  actionList,
  avatar,
  name,
  level,
  country,
  platform,
  clanTag,
}) => {
  return (
    <ProfileHeader rowGap={1}>
      <Stack direction={"row"} gap={2}>
        <Box sx={{ position: "relative" }}>
          <OnlineStatusBadge
            overlap="circular"
            anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
            variant="dot"
            isOnline={isOnline}
          >
            <Avatar src={avatar}>{name[0]}</Avatar>
          </OnlineStatusBadge>
        </Box>
        <Stack direction={"row"} justifyContent={"space-between"} flexGrow={1}>
          <Stack>
            <Typography
              textOverflow={"ellipsis"}
              fontSize={"1.125rem"}
              fontWeight={600}
              lineHeight={"1.25rem"}
              marginBottom={0.2}
            >
              <Link
                style={{ color: "inherit" }}
                to={`/records/players/${
                  player?.player_id ?? player?.profile?.player_id
                }`}
              >
                {name}
              </Link>
              {clanTag && (
                <Typography
                  sx={{ px: 0.5 }}
                  variant="caption"
                >{`[${clanTag}]`}</Typography>
              )}
            </Typography>
            <Box
              sx={{ display: "flex", alignItems: "center", marginBottom: 0.75 }}
            >
              <CopyableText
                text={player?.player_id ?? player?.profile?.player_id}
                size="0.75rem"
                sx={{ color: (theme) => theme.palette.text.secondary }}
              />
            </Box>
          </Stack>
          {actionList && (
            <ActionMenuButton
              recipients={player}
              actions={actionList}
              sx={{
                position: "absolute",
                top: (theme) => theme.spacing(0.5),
                right: (theme) => theme.spacing(0.5),
              }}
            />
          )}
        </Stack>
      </Stack>
      <Stack
        direction={"row"}
        gap={1}
        alignItems={"center"}
        justifyContent={"start"}
      >
        <LevelChip level={level} />
        <PlatformChip platform={platform} playerId={player.player_id} />
        <CountryChip country={country} />
      </Stack>
    </ProfileHeader>
  );
};

export default PlayerProfileHeader;
