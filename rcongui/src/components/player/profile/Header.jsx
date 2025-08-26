import { OnlineStatusBadge, ProfileHeader } from "./styled";
import { Avatar, Box, Typography, Stack, Chip } from "@mui/material";
import { Link } from "react-router-dom";
import { faSteam, faXbox } from "@fortawesome/free-brands-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import CopyableText from "@/components/shared/CopyableText";
import {
  isSteamPlayer,
  getSteamProfileUrl,
  levelToRank,
  toSnakeCase,
} from "@/utils/lib";
import { ActionMenu, ActionMenuButton } from "@/features/player-action/ActionMenu";
import { generatePlayerActions } from "@/features/player-action/actions";

const PlayerProfileHeader = ({
  player,
  isOnline,
  handleActionClick,
  actionList,
  avatar,
  name,
  level,
  country,
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
                  player?.player_id ?? profile.player_id
                }`}
              >
                {name}
              </Link>
            </Typography>
            <Box
              sx={{ display: "flex", alignItems: "center", marginBottom: 0.75 }}
            >
              <CopyableText
                text={player?.player_id ?? profile.player_id}
                size="0.75rem"
                sx={{ color: (theme) => theme.palette.text.secondary }}
              />
            </Box>
          </Stack>
          {actionList && handleActionClick && (
            <ActionMenuButton
              withProfile
              recipients={{ player_id: player.player_id, name }}
              actions={actionList}
            />
          )}
        </Stack>
      </Stack>
      <Stack direction={"row"} gap={1} alignItems={"center"}>
        {!!level && (
          <Chip
            avatar={
              <Avatar
                alt="Natacha"
                src={`/icons/ranks/${toSnakeCase(levelToRank(level))}.webp`}
              />
            }
            label={level}
          />
        )}
        {isSteamPlayer(player) ? (
          <Chip
            component={"a"}
            href={getSteamProfileUrl(player.player_id)}
            target="_blank"
            rel="noreferrer"
            icon={<FontAwesomeIcon icon={faSteam} />}
            label="Steam"
            sx={{ "&:hover": { cursor: "pointer" } }}
          />
        ) : (
          <Chip
            icon={<FontAwesomeIcon icon={faXbox} />}
            label="Other"
          />
        )}
        {country && (
          <Chip
            avatar={
              <Avatar
                alt="Natacha"
                src={`https://flagcdn.com/w20/${country.toLowerCase()}.png`}
              />
            }
            label={country}
            variant="outlined"
            size="small"
          />
        )}
      </Stack>
    </ProfileHeader>
  );
};

export default PlayerProfileHeader;
