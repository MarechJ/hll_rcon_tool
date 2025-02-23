import {
  Box,
  IconButton,
  Typography,
  Divider,
  Tabs,
  Tab,
  Stack,
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
import { Close, ConstructionOutlined } from "@mui/icons-material";
import { TabContext, TabPanel } from "@mui/lab";
import dayjs from "dayjs";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { useActionDialog } from "@/hooks/useActionDialog";
import { usePlayerSidebar } from "@/hooks/usePlayerSidebar";
import { generatePlayerActions } from "@/features/player-action/actions";
import { ClientError } from "../shared/ClientError";
import { useState } from "react";
import {
  ProfileHeader,
  ProfileWrapper,
  ResponsiveDrawer,
  Message,
} from "@/components/player/profile/styled";
import PlayerProfileHeader from "../player/profile/Header";
import PlayerProfileSummary from "../player/profile/Summary";
import PlayerProfileStatusTags from "../player/profile/StatusTags";

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
  const { openDialog } = useActionDialog();

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
      <PlayerProfileHeader
        player={player}
        isOnline={isOnline}
        onClose={onClose}
        handleActionClick={handleActionClick([player])}
        actionList={actionList}
        avatar={avatar}
        name={name}
      />
      <Divider />
      <PlayerProfileStatusTags
        isVip={isVip}
        isWatched={isWatched}
        isBlacklisted={isBlacklisted}
        isBanned={isBanned}
      />
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
          <PlayerProfileSummary
            country={player.country}
            firstSeen={profile.created ?? player.created}
            lastSeen={profile?.names[0]?.last_seen}
            sessionCount={profile.sessions_count ?? profile.sessions_count}
            flags={profile.flags ?? profile.flags}
            totalPlaytime={
              profile.total_playtime_seconds ?? profile.total_playtime_seconds
            }
            vip={playerVip}
            otherVips={profile.vip_lists}
            names={profile.names}
            watchlist={profile.watchlist}
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
