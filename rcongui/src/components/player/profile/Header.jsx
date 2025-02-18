import { OnlineStatusBadge, ProfileHeader } from "./styled";
import { Avatar, Box, IconButton, Typography, Button } from "@mui/material";
import { Link } from "react-router-dom";
import { faSteam } from "@fortawesome/free-brands-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import CopyableText from "@/components/shared/CopyableText";
import { isSteamPlayer, getSteamProfileUrl } from "@/utils/lib";
import CloseIcon from "@mui/icons-material/Close";
import SportsEsportsIcon from "@mui/icons-material/SportsEsports";
import { ActionMenu } from "@/features/player-action/ActionMenu";

const PlayerProfileHeader = ({ player, isOnline, onClose, handleActionClick, actionList, avatar, name }) => {
  return (
    <ProfileHeader rowGap={1}>
      <OnlineStatusBadge
        overlap="circular"
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
        variant="dot"
        isOnline={isOnline}
      >
        <Avatar src={avatar}>{name[0]}</Avatar>
      </OnlineStatusBadge>
      <Box sx={{ flexGrow: 1 }}>
        <Typography
          component={"h1"}
          variant="h6"
          sx={{ textOverflow: "ellipsis" }}
        >
          <Link
            style={{ color: "inherit" }}
            to={`/records/players/${player?.player_id ?? profile.player_id}`}
          >
            {name}
          </Link>
        </Typography>
        <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
          <CopyableText text={player?.player_id ?? profile.player_id} />
        </Box>
        <Box>
          {isSteamPlayer(player) && (
            <Button
              variant={"outline"}
              LinkComponent={"a"}
              href={getSteamProfileUrl(player.player_id)}
              target="_blank"
              rel="noreferrer"
            >
              <FontAwesomeIcon icon={faSteam} />
            </Button>
          )}
          {!isSteamPlayer(player) && <SportsEsportsIcon />}
        </Box>
      </Box>
      {onClose && (
        <IconButton
          sx={{
            position: "absolute",
            top: (theme) => theme.spacing(0.5),
            right: (theme) => theme.spacing(0.5),
          }}
        size="small"
          onClick={onClose}
        >
          <CloseIcon />
        </IconButton>
      )}
      <ActionMenu
        handleActionClick={handleActionClick}
        actionList={actionList}
        sx={{
          position: "absolute",
          top: (theme) => theme.spacing(0.5),
          left: (theme) => theme.spacing(0.5),
        }}
      />
    </ProfileHeader>
  );
};

export default PlayerProfileHeader;
