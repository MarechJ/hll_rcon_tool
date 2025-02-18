import {
    Box,
    Typography,
    Divider,
    Stack,
  } from "@mui/material";
  import dayjs from "dayjs";
  import VisibilityIcon from "@mui/icons-material/Visibility";
  import { Chip } from "@mui/material";
  import CalendarTodayIcon from "@mui/icons-material/CalendarToday";
  import WorkspacePremiumIcon from "@mui/icons-material/WorkspacePremium";
  import PersonIcon from "@mui/icons-material/Person";
  import FlagIcon from "@mui/icons-material/Flag";
  import FlagList from "./FlagList";
  import WatchlistList from "./WatchlistList";
  import VipList from "./VipList";

const PlayerProfileSummary = ({
  firstSeen,
  lastSeen,
  vip,
  otherVips,
  sessionCount,
  flags,
  totalPlaytime,
  names,
  watchlist,
}) => {
  return (
    <Stack spacing={3}>
      <Box component="section">
        <Typography
          variant="h6"
          sx={{ mb: 1, display: "flex", alignItems: "center", gap: 1 }}
        >
          <FlagIcon /> Flags
        </Typography>
        <FlagList flags={flags} />
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
          <Typography>
            Playtime: {Math.floor(totalPlaytime / 3600)} hours
          </Typography>
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
        <VipList vip={vip} otherVips={otherVips} />
      </Box>

      <Divider />

      <Box component="section">
        <Typography
          variant="h6"
          sx={{ mb: 1, display: "flex", alignItems: "center", gap: 1 }}
        >
          <VisibilityIcon /> Watchlist
        </Typography>
        <WatchlistList watchlist={watchlist} />
      </Box>

      <Divider />

      <Box component="section">
        <Typography
          variant="h6"
          sx={{ mb: 1, display: "flex", alignItems: "center", gap: 1 }}
        >
          <PersonIcon /> Also known as
        </Typography>
        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
          {names?.map((nameObj) => (
            <Chip
              key={nameObj.id}
              label={nameObj.name}
              variant="outlined"
              size="small"
            />
          ))}
        </Box>
      </Box>
    </Stack>
  );
};

export default PlayerProfileSummary;
