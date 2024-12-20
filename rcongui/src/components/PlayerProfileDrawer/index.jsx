import {
  Box,
  IconButton,
  Typography,
  Drawer,
  Toolbar,
  Divider,
  Avatar,
  Tabs,
  Tab,
  Stack,
  Badge,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  AccordionActions,
  Button,
  Skeleton,
  Paper,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
} from "@mui/material";
import { Close } from "@mui/icons-material";
import { TabContext, TabPanel } from "@mui/lab";
import { styled, useMediaQuery } from "@mui/system";
import { ActionMenu } from "@/features/player-action/ActionMenu";
import dayjs from "dayjs";
import StarIcon from "@mui/icons-material/Star";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import VisibilityIcon from "@mui/icons-material/Visibility";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import NoAccountsIcon from "@mui/icons-material/NoAccounts";
import GavelIcon from "@mui/icons-material/Gavel";
import { green, red, yellow } from "@mui/material/colors";
import { useActionDialog } from "@/hooks/useActionDialog";
import { usePlayerSidebar } from "@/hooks/usePlayerSidebar";
import { generatePlayerActions } from "@/features/player-action/actions";
import { ClientError } from "../shared/ClientError";
import { useState } from "react";
import {
  getSteamProfileUrl,
  getXboxProfileUrl,
  isSteamPlayer,
} from "@/utils/lib";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSteam, faXbox } from "@fortawesome/free-brands-svg-icons";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import DoneAllIcon from "@mui/icons-material/DoneAll";
import { Link } from "react-router-dom";
import { Chip } from "@mui/material";
import CalendarTodayIcon from "@mui/icons-material/CalendarToday";
import WorkspacePremiumIcon from "@mui/icons-material/WorkspacePremium";
import PersonIcon from "@mui/icons-material/Person";
import PublicIcon from '@mui/icons-material/Public';
import FlagIcon from '@mui/icons-material/Flag';

const OnlineStatusBadge = styled(Badge, {
  shouldForwardProp: (props) => props !== "isOnline",
})(({ theme, isOnline }) => ({
  "& .MuiBadge-badge": {
    backgroundColor: isOnline ? green["500"] : red["500"],
    color: isOnline ? green["500"] : red["500"],
    boxShadow: `0 0 0 2px ${theme.palette.background.paper}`,
    "&::after": {
      position: "absolute",
      top: 0,
      left: 0,
      width: "100%",
      height: "100%",
      borderRadius: "50%",
      animation: isOnline ? "ripple 1.2s infinite ease-in-out" : "none",
      border: "1px solid currentColor",
      content: '""',
    },
  },
  "@keyframes ripple": {
    "0%": {
      transform: "scale(.8)",
      opacity: 1,
    },
    "100%": {
      transform: "scale(2.4)",
      opacity: 0,
    },
  },
}));

const ResponsiveDrawer = styled(Drawer)(({ theme }) => ({
  "& .MuiDrawer-paper": {
    width: "100%",
    [theme.breakpoints.up("sm")]: {
      width: "30rem",
    },
  },
}));

const ProfileWrapper = styled(Box)(({ theme }) => ({
  width: "100%",
  height: "100%",
  overflowX: "hidden",
  paddingTop: theme.spacing(1),
  paddingBottom: theme.spacing(2),
  [theme.breakpoints.up("sm")]: {
    width: "30rem",
  },
}));

const ProfileHeader = styled(Stack)(({ theme }) => ({
  paddingRight: theme.spacing(1),
  paddingLeft: theme.spacing(2),
  paddingTop: theme.spacing(2),
  marginBottom: theme.spacing(1),
  alignItems: "center",
  textAlign: "center",
  position: "relative",
}));

const Message = styled(Box)(({ theme }) => ({
  background:
    theme.palette.mode === "dark"
      ? theme.palette.primary.dark
      : theme.palette.primary.light,
  color: theme.palette.primary.contrastText,
  paddingTop: theme.spacing(1),
  paddingBottom: theme.spacing(1),
  paddingRight: theme.spacing(1.5),
  paddingLeft: theme.spacing(1.5),
  borderRadius: theme.shape.borderRadius,
  borderBottomRightRadius: 0,
}));

const BasicProfileDetails = ({
  firstSeen,
  lastSeen,
  country,
  vip,
  sessionCount,
  flags,
  totalPlaytime,
  names,
}) => {
  return (
    <Stack spacing={3}>
      <Box component="section">
        <Typography
          variant="h6"
          sx={{ mb: 1, display: "flex", alignItems: "center", gap: 1 }}
        >
          <PublicIcon /> Location
        </Typography>
        <Typography>{country ?? "Unknown"}</Typography>
      </Box>

      <Divider />

      <Box component="section">
        <Typography
          variant="h6"
          sx={{ mb: 1, display: "flex", alignItems: "center", gap: 1 }}
        >
          <FlagIcon /> Flags
        </Typography>
        {flags.map(({ flag, comment, modified }) => (
          <Stack key={flag}>
            <Typography>{flag} - {comment}</Typography>
            <Typography>Modified: {dayjs(modified).format("LLL")}</Typography>
          </Stack>
        ))}
      </Box>

      <Divider />

      <Box component="section">
        <Typography
          variant="h6"
          sx={{ mb: 1, display: "flex", alignItems: "center", gap: 1 }}
        >
          <CalendarTodayIcon /> Activity
        </Typography>
        <Stack spacing={0.5}>
          <Typography>First Seen: {dayjs(firstSeen).format("LLL")}</Typography>
          <Typography>Last Seen: {dayjs(lastSeen).format("LLL")}</Typography>
          <Typography>Visits: {sessionCount}</Typography>
          <Typography>Playtime: {Math.floor(totalPlaytime / 3600)} hours</Typography>
        </Stack>
      </Box>

      <Divider />

      <Box component="section">
        <Typography
          variant="h6"
          sx={{ mb: 1, display: "flex", alignItems: "center", gap: 1 }}
        >
          <WorkspacePremiumIcon /> VIP Status
        </Typography>
        <Stack spacing={0.5}>
          <div>
            <Chip
              label={vip ? "VIP" : "Non-VIP"}
              color={vip ? "primary" : "default"}
              variant={vip ? "filled" : "outlined"}
            />
          </div>
          {vip && (
            <Typography variant="body2">
              Expires: {dayjs(vip.expiration).format("LLL")}
            </Typography>
          )}
        </Stack>
      </Box>

      <Divider />

      <Box component="section">
        <Typography
          variant="h6"
          sx={{ mb: 1, display: "flex", alignItems: "center", gap: 1 }}
        >
          <PersonIcon /> Known Names
        </Typography>
        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
          {names?.map((nameObj) => (
            <Chip key={nameObj.id} label={nameObj.name} variant="outlined" size="small" />
          ))}
        </Box>
      </Box>
    </Stack>
  );
};

const Penalties = ({ punish, kick, tempBan, parmaBan }) => (
  <dl>
    <dt>Punish</dt>
    <dd>{punish ?? 0}</dd>
    <dt>Kick</dt>
    <dd>{kick ?? 0}</dd>
    <dt>Temporary ban</dt>
    <dd>{tempBan ?? 0}</dd>
    <dt>Permanent ban</dt>
    <dd>{parmaBan ?? 0}</dd>
  </dl>
);

const ReceivedActions = ({ actions }) => {
  const [expanded, setExpanded] = useState(false);
  const displayCount = expanded ? actions.length : 2;

  return (
    <>
      {actions.slice(0, displayCount).map((action, i) => (
        <Accordion square={true} key={action.action_type + i}>
          <AccordionSummary
            expandIcon={<ArrowDropDownIcon />}
            aria-controls={`panel${i}-content`}
            id={`panel${i}-header`}
          >
            <Box sx={{ display: "flex", flexDirection: "column" }}>
              <Typography variant="subtitle2">{action.action_type}</Typography>
              <Typography component={"span"} sx={{ fontSize: "0.7rem" }}>
                {action.by} | {dayjs(action.time).format("HH:MM DD.MM.YY")}
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Typography>{action.reason}</Typography>
          </AccordionDetails>
        </Accordion>
      ))}
      <Accordion defaultExpanded>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel-action-content"
          id="panel-action-header"
        >
          Show all
        </AccordionSummary>
        <AccordionDetails>
          {`This player received ${actions.length} actions in total.`}
        </AccordionDetails>
        <AccordionActions>
          <Button onClick={() => setExpanded((prevState) => !prevState)}>
            {expanded ? "Hide" : "Show"}
          </Button>
        </AccordionActions>
      </Accordion>
    </>
  );
};

const Messages = ({ messages }) => {
  return (
    <>
      {messages && messages.length ? (
        <Stack spacing={1.5}>
          {messages.map((message, index) => (
            <Message key={message.time}>
              <Typography component={"span"} sx={{ fontSize: "0.7rem" }}>
                {message.by} | {dayjs(message.time).format("HH:MM DD.MM.YY")}
              </Typography>
              <Typography>{message.reason}</Typography>
            </Message>
          ))}
        </Stack>
      ) : (
        <Box>
          <Typography variant="subtitle" component={"span"}>
            No messages
          </Typography>
        </Box>
      )}
    </>
  );
};

const LoadingSkeleton = ({ onClose }) => (
  <DrawerBase onClose={onClose}>
    <Stack gap={2} justifyContent={"center"} alignItems={"center"}>
      <Skeleton variant="circular" width={40} height={40} />
      <Divider orientation="horizontal" flexItem />
      <Skeleton variant="rectangular" width={210} height={60} />
      <Skeleton variant="rounded" width={210} height={60} />
    </Stack>
  </DrawerBase>
);

const DrawerBase = ({ children, onClose }) => (
  <ProfileWrapper>
    <ProfileHeader>
      <IconButton
        sx={{
          position: "absolute",
          top: (theme) => theme.spacing(0.5),
          right: (theme) => theme.spacing(0.5),
        }}
        size="small"
        onClick={onClose}
      >
        <Close />
      </IconButton>
    </ProfileHeader>
    <Box component={"section"} sx={{ p: 2 }}>
      {children}
    </Box>
  </ProfileWrapper>
);

const ProfileNotFound = ({ onClose }) => (
  <DrawerBase onClose={onClose}>
    <Box
      sx={{
        display: "grid",
        alignContent: "center",
        height: "100%",
        width: "100%",
      }}
    >
      <Typography variant="h6" sx={{ textAlign: "center" }}>
        Profile not found
      </Typography>
    </Box>
  </DrawerBase>
);

const ProfileError = ({ error, onClose }) => (
  <DrawerBase onClose={onClose}>
    <ClientError error={error} />
  </DrawerBase>
);

const PlayerDetails = ({ player, onClose }) => {
  const [openedTab, setOpenedTab] = useState("profile");
  const [copySuccess, setCopySuccess] = useState(false);
  const { openDialog } = useActionDialog();

  const handleCopyId = async () => {
    const id = player?.player_id ?? profile.player_id;
    try {
      await navigator.clipboard.writeText(id);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch (err) {
      console.error("Failed to copy ID:", err);
    }
  };

  const handleActionClick = (recipients) => (action) => {
    openDialog(action, recipients);
  };

  const handleTabChange = (event, newValue) => {
    setOpenedTab(newValue);
  };

  const profile = player.profile;
  const isOnline = player?.is_online;
  const isVip = player?.is_vip;
  const playerVip = player?.vip;
  const isWatched = profile?.watchlist && profile?.watchlist?.is_watched;
  const isBlacklisted = profile?.is_blacklisted;
  const isBanned = profile?.is_banned;
  const actionList = generatePlayerActions({
    multiAction: false,
    onlineAction: isOnline,
  });
  const name = player?.name ?? profile.names[0]?.name ?? "?";
  const avatar = profile?.steaminfo?.profile?.avatar;

  return (
    <ProfileWrapper component={"article"}>
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
            <Typography variant="subtitle2">
              ID: {player?.player_id ?? profile.player_id}
            </Typography>
            <IconButton
              size="small"
              onClick={handleCopyId}
              sx={{
                padding: "2px",
                "& .MuiSvgIcon-root": {
                  fontSize: "0.9rem",
                },
              }}
            >
              {copySuccess ? (
                <DoneAllIcon sx={{ color: green["500"] }} />
              ) : (
                <ContentCopyIcon />
              )}
            </IconButton>
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
            {!isSteamPlayer(player) && (
              <Button
                variant={"outline"}
                LinkComponent={"a"}
                href={getXboxProfileUrl(player.name)}
                target="_blank"
                rel="noreferrer"
              >
                <FontAwesomeIcon icon={faXbox} />
              </Button>
            )}
          </Box>
        </Box>
        <IconButton
          sx={{
            position: "absolute",
            top: (theme) => theme.spacing(0.5),
            right: (theme) => theme.spacing(0.5),
          }}
          size="small"
          onClick={onClose}
        >
          <Close />
        </IconButton>
        <ActionMenu
          handleActionClick={handleActionClick([player])}
          actionList={actionList}
          sx={{
            position: "absolute",
            top: (theme) => theme.spacing(0.5),
            left: (theme) => theme.spacing(0.5),
          }}
        />
      </ProfileHeader>
      <Divider />
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
      <Divider />
      <TabContext value={openedTab}>
        <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
          <Tabs
            value={openedTab}
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
            aria-label="Player details"
          >
            <Tab label="Profile" value="profile" />
            {isOnline && <Tab label="Game" value="game" />}
            <Tab label="Admin" value="admin" />
            <Tab
              label="Messages"
              value="messages"
              disabled={
                profile.received_actions.filter(
                  (action) => action.action_type === "MESSAGE"
                ).length === 0
              }
            />
            <Tab
              label="Comments"
              value="comments"
              disabled={player.comments.length === 0}
            />
            <Tab
              label="Bans"
              value="bans"
              disabled={player.bans.length === 0}
            />
            <Tab label="Logs" value="logs" disabled={true} />
          </Tabs>
        </Box>
        <TabPanel value="profile">
          <BasicProfileDetails
            country={player.country}
            firstSeen={profile.created ?? player.created}
            lastSeen={profile?.names[0]?.last_seen}
            sessionCount={profile.sessions_count ?? profile.sessions_count}
            flags={profile.flags ?? profile.flags}
            totalPlaytime={
              profile.total_playtime_seconds ?? profile.total_playtime_seconds
            }
            vip={playerVip}
            names={profile.names}
          />
        </TabPanel>
        {isOnline && (
          <TabPanel value="game">
            <PlayerGameDetails player={player} />
          </TabPanel>
        )}
        <TabPanel value="admin">
          <Box component={"section"}>
            <Typography variant="h6" component={"h2"}>
              Penalties
            </Typography>
            <Penalties
              punish={profile.penalty_count["PUNISH"]}
              kick={profile.penalty_count["KICK"]}
              tempBan={profile.penalty_count["TEMPBAN"]}
              parmaBan={profile.penalty_count["PERMABAN"]}
            />
          </Box>
          <Box component={"section"}>
            <Typography variant="h6" component={"h2"}>
              Received actions
            </Typography>
            <ReceivedActions actions={profile.received_actions} />
          </Box>
        </TabPanel>
        <TabPanel value="messages">
          <Box component={"section"}>
            <Typography variant="h6" component={"h2"}>
              Messages
            </Typography>
            <Messages
              messages={profile.received_actions.filter(
                (action) => action.action_type === "MESSAGE"
              )}
            />
          </Box>
        </TabPanel>
        <TabPanel value="comments">
          <Comments comments={player.comments} />
        </TabPanel>
        <TabPanel value="bans">
          <Bans bans={player.bans} />
        </TabPanel>
      </TabContext>
    </ProfileWrapper>
  );
};

const Comments = ({ comments }) => {
  return (
    <Box component={"section"}>
      <Typography variant="h6" component={"h2"}>
        Comments
      </Typography>
      <Stack sx={{ gap: 1 }}>
        {comments.map((comment) => (
          <Comment key={comment.id} comment={comment} />
        ))}
      </Stack>
    </Box>
  );
};

const Comment = ({ comment }) => {
  return (
    <Box component={Paper} sx={{ p: 1 }}>
      <Typography>{comment.content}</Typography>
      <Divider sx={{ my: 1 }} />
      <Typography sx={{ fontSize: "0.7rem" }} variant="subtitle2">
        {comment.by} | {dayjs(comment.creation_time).format("HH:MM DD.MM.YY")}
      </Typography>
    </Box>
  );
};

const Bans = ({ bans }) => {
  return (
    <Box component={"section"}>
      <Typography variant="h6" component={"h2"}>
        Bans
      </Typography>
      <Stack sx={{ gap: 1 }}>
        {bans.map((ban) => (
          <Ban key={ban.id} ban={ban} />
        ))}
      </Stack>
    </Box>
  );
};

const Ban = ({ ban }) => {
  return (
    <Box component={Paper} sx={{ p: 1 }}>
      <Typography variant="subtitle">{ban.type}</Typography>
      <Typography>{ban.reason}</Typography>
      <Divider sx={{ my: 1 }} />
      <Typography sx={{ fontSize: "0.7rem" }} variant="subtitle2">
        {ban.by} | {dayjs(ban.ban_time).format("HH:MM DD.MM.YY")}
      </Typography>
    </Box>
  );
};

const PlayerGameDetails = ({ player }) => {
  return (
    <Box component={"section"}>
      <Typography variant="h6" component={"h2"}>
        Current Game Stats
      </Typography>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Stat</TableCell>
            <TableCell>Value</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {[
            "level",
            "unit",
            "loadout",
            "team",
            "role",
            "kills",
            "deaths",
            "combat",
            "offense",
            "defense",
            "support",
          ].map((stat) => (
            <TableRow key={stat}>
              <TableCell>{stat}</TableCell>
              <TableCell>{player[stat] ?? "-"}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Box>
  );
};

export const PlayerDetailDrawer = () => {
  const { open, close, player, isLoading, profileError } = usePlayerSidebar();

  return (
    <ResponsiveDrawer
      variant="persistent"
      open={open}
      anchor="right"
      onClose={close}
    >
      <Toolbar />
      {isLoading && !player ? (
        <LoadingSkeleton onClose={close} />
      ) : profileError ? (
        <ProfileError error={profileError} onClose={close} />
      ) : !!player ? (
        <PlayerDetails player={player} onClose={close} />
      ) : open && !player ? (
        <ProfileNotFound onClose={close} />
      ) : null}
    </ResponsiveDrawer>
  );
};
