import { OnlineStatusBadge, ProfileHeader } from "./styled";
import { Avatar, Box, Typography, Stack } from "@mui/material";
import { Link } from "react-router-dom";
import CopyableText from "@/components/shared/CopyableText";
import PlatformChip from "./Platform";
import CountryChip from "./Country";
import LevelChip from "./Level";
import LinksChip from "./Links";

const PlayerProfileHeader = ({
  player,
  isOnline,
  ActionList,
  avatar,
  name,
  level,
  country,
  platform,
  clanTag,
}) => {
  const currentSoldierData = player?.soldier ?? player?.profile?.soldier;
  const playerId = player?.player_id ?? player?.profile?.player_id;
  const currentAccountData = player?.account ?? player?.profile?.account;
  return (
    <ProfileHeader gap={0.5}>
      <Stack>
        <Stack direction={"row"} spacing={1}>
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
          <Stack
            direction={"row"}
            justifyContent={"space-between"}
            flexGrow={1}
          >
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
                    playerId
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
                sx={{
                  display: "flex",
                  alignItems: "center",
                  marginBottom: 0.75,
                }}
              >
                <CopyableText
                  text={playerId}
                  size="0.75rem"
                  sx={{ color: (theme) => theme.palette.text.secondary }}
                />
              </Box>
            </Stack>
          </Stack>
          {ActionList && <ActionList />}
        </Stack>
        <Stack
          direction={"row"}
          gap={1}
          alignItems={"center"}
          justifyContent={"start"}
        >
          <LevelChip level={level} playerId={playerId} currentSoldierData={currentSoldierData} />
          <PlatformChip platform={platform} playerId={playerId} currentSoldierData={currentSoldierData} />
          <CountryChip country={country} playerId={playerId} currentAccountData={currentAccountData} />
          <LinksChip playerId={playerId} />
        </Stack>
      </Stack>
    </ProfileHeader>
  );
};

export default PlayerProfileHeader;