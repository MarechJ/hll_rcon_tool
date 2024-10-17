import React, { useEffect } from "react";
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
} from "@mui/material";
import { Close } from "@mui/icons-material";
import { TabContext, TabPanel } from "@mui/lab";
import { styled } from "@mui/system";
import ActionMenu from "@/features/player-action/ActionMenu";
import dayjs from "dayjs";
import CheckIcon from "@mui/icons-material/Check";
import CloseIcon from "@mui/icons-material/Close";
import StarIcon from "@mui/icons-material/Star";
import ArrowDownwardIcon from "@mui/icons-material/ArrowDownward";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import VisibilityIcon from "@mui/icons-material/Visibility";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import NoAccountsIcon from "@mui/icons-material/NoAccounts";
import GavelIcon from "@mui/icons-material/Gavel";
import { green, red } from "@mui/material/colors";
import { useActionDialog } from "@/hooks/useActionDialog";
import { usePlayerSidebar } from "@/hooks/usePlayerSidebar";
import { CountryFlag } from "../CountryFlag";
import { get } from "@/utils/fetchUtils";
import {
  playerGameActions,
  playerProfileActions,
} from "@/features/player-action/actions";

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
  width: "100%",
  [theme.breakpoints.up("md")]: {
    width: "30rem",
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
}) => {
  return (
    <dl>
      <dt>Country</dt>
      <dd>
        {country && country !== "private" ? (
          <>
            <CountryFlag country={country} />
            <span style={{ marginLeft: 4 }}>{country}</span>
          </>
        ) : (
          "Unknown"
        )}
      </dd>
      <dt>First Seen</dt>
      <dd>{firstSeen ? dayjs(firstSeen).format("MMM DD, YYYY") : "N/A"}</dd>
      <dt>Last Seen</dt>
      <dd>{lastSeen ? dayjs(lastSeen).format("MMM DD, YYYY") : "N/A"}</dd>
      <dt>VIP</dt>
      <dd>{vip ? "Yes" : "No"}</dd>
      {vip && (
        <>
          <dt>VIP Expires</dt>
          <dd>{dayjs(vip.expiration).fromNow()}</dd>
          <dd>{dayjs(vip.expiration).format("mm:HH MM DD, YYYY")}</dd>
        </>
      )}
      <dt>Visits</dt>
      <dd>{sessionCount}</dd>
      <dt>Playtime in hours</dt>
      <dd>{Math.round(totalPlaytime / 3600)}</dd>
      {flags.length > 0 && (
        <>
          <dt>Flags</dt>
          <dd>
            <dl>
              {flags.map(({ flag, comment: note, modified }, index) => (
                <React.Fragment key={flag + index}>
                  {index ? <Divider /> : null}
                  <dt>{flag}</dt>
                  <dd>
                    Created:{" "}
                    {modified ? dayjs(modified).format("HH:MM DD.MM.YY") : ""}
                  </dd>
                  {note ? <dd>Note: {note}</dd> : null}
                </React.Fragment>
              ))}
            </dl>
          </dd>
        </>
      )}
    </dl>
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
  const [expanded, setExpanded] = React.useState(false);
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
            {action.comment && <Typography>{action.comment}</Typography>}
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

export const PlayerDetailDrawer = () => {
  const [openedTab, setOpenedTab] = React.useState("1");

  const { openDialog } = useActionDialog();

  const { open, setOpen, player, isFetching } = usePlayerSidebar();

  const [comments, setComments] = React.useState([]);
  const [bans, setBans] = React.useState([]);

  // TODO
  // Move up to the sidebar provider
  useEffect(() => {
    const fetchComments = async () => {
      const response = await get(
        "get_player_comment?player_id=" + player.player_id
      );
      const json = await response.json();
      const comments = json.result;
      if (comments && typeof comments === "object" && comments.length > 0) {
        setComments(comments);
      }
    };

    open && player && fetchComments();
  }, [player, open]);

  useEffect(() => {
    const fetchBans = async () => {
      const response = await get("get_ban?player_id=" + player.player_id);
      const json = await response.json();
      const bans = json.result;
      if (bans && typeof bans === "object" && bans.length > 0) {
        setBans(bans);
      }
    };

    open && player && fetchBans();
  }, [player, open]);

  let receivedActions = player?.profile?.received_actions;

  if (receivedActions && comments.length > 0) {
    const ACTION_COMMENT_CREATION_GAP = 200;
    receivedActions = receivedActions.map((action) => {
      const commentMatch = comments.find((comment) => {
        const commentCreated = new Date(comment.creation_time);
        const actionCreated = new Date(action.time);
        const createdDifference = Math.abs(commentCreated - actionCreated);
        return createdDifference < ACTION_COMMENT_CREATION_GAP;
      });
      return { ...action, comment: commentMatch };
    });
  }

  const handleActionClick = (recipients) => (action) => {
    openDialog(action, recipients);
  };

  const handleTabChange = (event, newValue) => {
    setOpenedTab(newValue);
  };
  // TODO
  // Move this also to the sidebar provider?
  const isOnline = player?.profile?.sessions?.[0]?.end ?? false;
  const isWatched =
    player?.profile?.watchlist && player?.profile?.watchlist?.is_watched;
  const isBlacklisted =
    player?.profile?.blacklist && player?.profile?.blacklist?.is_blacklisted;
  const isBanned = bans.length > 0;
  const actionList = isOnline ? playerGameActions : playerProfileActions;
  // TODO
  const playerVip = false;

  return (
    <ResponsiveDrawer
      variant="persistent"
      open={open}
      anchor="right"
      onClose={() => setOpen(false)}
    >
      <Toolbar />
      {isFetching ? (
        <ProfileWrapper>
          <ProfileHeader>
            <IconButton
              sx={{
                position: "absolute",
                top: (theme) => theme.spacing(0.5),
                right: (theme) => theme.spacing(0.5),
              }}
              size="small"
              onClick={() => setOpen(false)}
            >
              <Close />
            </IconButton>
          </ProfileHeader>
          <Stack gap={2} justifyContent={"center"} alignItems={"center"}>
            <Skeleton variant="circular" width={40} height={40} />
            <Divider orientation="horizontal" flexItem />
            <Skeleton variant="rectangular" width={210} height={60} />
            <Skeleton variant="rounded" width={210} height={60} />
          </Stack>
        </ProfileWrapper>
      ) : !!player ? (
        <ProfileWrapper component={"article"}>
          <ProfileHeader rowGap={1}>
            <OnlineStatusBadge
              overlap="circular"
              anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
              variant="dot"
              isOnline={isOnline}
            >
              <Avatar src={player.profile?.steaminfo?.profile?.avatar ?? player?.steaminfo?.profile?.avatar}>
                {player?.names[0]?.name[0] ?? player?.profile?.names[0]?.name[0] ?? "?"}
              </Avatar>
            </OnlineStatusBadge>
            <Box sx={{ flexGrow: 1 }}>
              <Typography
                component={"h1"}
                variant="h6"
                sx={{ textOverflow: "ellipsis" }}
              >
                {player?.names[0]?.name ?? player?.profile?.names[0]?.name ?? "Unknown"}
              </Typography>
              <Typography variant="subtitle2">
                ID: {player.player_id}
              </Typography>
            </Box>
            <IconButton
              sx={{
                position: "absolute",
                top: (theme) => theme.spacing(0.5),
                right: (theme) => theme.spacing(0.5),
              }}
              size="small"
              onClick={() => setOpen(false)}
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
            {playerVip && <StarIcon />}
            {isWatched && <VisibilityIcon />}
            {isBlacklisted && <NoAccountsIcon />}
            {isBanned && <GavelIcon />}
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
                <Tab label="Profile" value="1" />
                <Tab label="Admin" value="2" />
                <Tab label="Messages" value="3" />
              </Tabs>
            </Box>
            <TabPanel value="1">
              <BasicProfileDetails
                country={player.country}
                firstSeen={player?.profile?.created ?? player.created}
                lastSeen={player?.profile?.names[0]?.last_seen ?? player?.names[0]?.last_seen}
                sessionCount={player?.profile?.sessions_count ?? player?.sessions_count}
                flags={player?.profile?.flags ?? player?.flags}
                totalPlaytime={player?.profile?.total_playtime_seconds ?? player?.total_playtime_seconds}
                vip={playerVip}
              />
            </TabPanel>
            <TabPanel value="2">
              <Box component={"section"}>
                <Typography variant="h6" component={"h2"}>
                  Penalties
                </Typography>
                <Penalties
                  punish={player?.profile?.penalty_count["PUNISH"]}
                  kick={player?.profile?.penalty_count["KICK"]}
                  tempBan={player?.profile?.penalty_count["TEMPBAN"]}
                  parmaBan={player?.profile?.penalty_count["PERMABAN"]}
                />
              </Box>
              <Box component={"section"}>
                <Typography variant="h6" component={"h2"}>
                  Received actions
                </Typography>
                <ReceivedActions actions={receivedActions} />
              </Box>
            </TabPanel>
            <TabPanel value="3">
              <Box component={"section"}>
                <Typography variant="h6" component={"h2"}>
                  Messages
                </Typography>
                <Messages
                  messages={player?.profile?.received_actions.filter(
                    (action) => action.action_type === "MESSAGE"
                  )}
                />
              </Box>
            </TabPanel>
          </TabContext>
        </ProfileWrapper>
      ) : open && !player ? (
        <ProfileWrapper>
          <ProfileHeader>
            <IconButton
              sx={{
                position: "absolute",
                top: (theme) => theme.spacing(0.5),
                right: (theme) => theme.spacing(0.5),
              }}
              size="small"
              onClick={() => setOpen(false)}
            >
              <Close />
            </IconButton>
          </ProfileHeader>
          <Box
            sx={{
              display: "grid",
              alignContent: "center",
              height: "100%",
              width: "100%",
            }}
          >
            <Typography variant="h6" sx={{ textAlign: "center" }}>
              Player not found
            </Typography>
          </Box>
        </ProfileWrapper>
      ) : null}
    </ResponsiveDrawer>
  );
};
