import { blue, green, grey, purple, red, yellow } from "@mui/material/colors";
import dayjs from "dayjs";

export const TEMPLATE_CATEGORY = {
  WELCOME: "WELCOME",
  BROADCAST: "BROADCAST",
  MESSAGE: "MESSAGE",
  REASON: "REASON",
  AUTO_SETTINGS: "AUTO_SETTINGS",
};

export const NEVER_EXPIRES_VIP_DATE = "3000-01-01T00:00:00+00:00";

export const unpackBroadcastMessage = (message) =>
  message.length
    ? message.split("\n").map((line) => {
        const regex = /(\d+)\s+(.*)/;
        const match = line.match(regex);
        if (!match) return { time_sec: "", message: "" };
        const [_, time_sec, content] = match;
        return { time_sec, message: content };
      })
    : [];

export const parseBroadcastMessages = (messages) =>
  messages.reduce((acc, msg, index, arr) => {
    let str = acc + `${msg.time_sec} ${msg.message}`;
    str += index !== arr.length - 1 ? "\n" : "";
    return str;
  }, "");

export const parseVotekickThresholds = (thresholds) => {
  const regex = /(\(\d+, \d+\))/g;
  const matches = thresholds.match(regex);
  if (!matches) return [];
  const result = matches.map((match) =>
    match.slice(1, -1).split(", ").map(Number)
  );
  return result;
};

export const getVipExpirationStatus = (vip) => {
  if (!vip) return "none";
  if (
    vip.vip_expiration === NEVER_EXPIRES_VIP_DATE ||
    vip.vip_expiration === null
  )
    return "never";
  if (dayjs(vip.vip_expiration).isBefore(dayjs())) return "expired";
  return "active";
};

export const getVipExpirationStatusColor = (status) => {
  switch (status) {
    case "never":
      return purple[500];
    case "expired":
      return red[500];
    case "active":
      return green[500];
    default:
      return grey[500];
  }
};

export const mapIdsToLayers = (layers, ids) => {
  if (!layers.length) return [];
  return ids
    .map((id) => layers.find((layer) => layer.id === id))
    .filter((layer) => layer !== undefined);
};

export const normalizePlayerProfile = (profile) => {
  profile = profile ?? {};

  return {
    ...profile,
    received_actions: profile.received_actions ?? [],
    vips: profile.vips ?? [],
    blacklists: profile.blacklists ?? [],
    watchlist: profile.watchlist ?? [],
    flags: profile.flags ?? [],
    penalty_count: profile.penalty_count ?? {
      KICK: 0,
      PUNISH: 0,
      TEMPBAN: 0,
      PERMABAN: 0,
    },
    sessions: profile.sessions ?? [],
    sessions_count: profile.sessions_count ?? 0,
    total_playtime_seconds: profile.total_playtime_seconds ?? 0,
    current_playtime_seconds: profile.current_playtime_seconds ?? 0,
    names: profile.names ?? [],
    bans: profile.bans ?? [],
  };
};

// https://hellletloose.fandom.com/wiki/Career_level
export const levelToRank = (level) => {
  if (level < 20) return "Private";
  if (level < 30) return "Private First Class";
  if (level < 40) return "Corporal";
  if (level < 50) return "Sergeant";
  if (level < 60) return "Staff Sergeant";
  if (level < 70) return "First Sergeant";
  if (level < 80) return "Master Sergeant";
  if (level < 90) return "2nd Lieutenant";
  if (level < 100) return "1st Lieutenant";
  if (level < 150) return "Captain";
  if (level < 200) return "Major";
  if (level < 250) return "Lieutenant Colonel";
  if (level < 300) return "Colonel";
  if (level < 350) return "Brigadier General";
  if (level < 400) return "Major General";
  if (level < 450) return "Lieutenant General";
  if (level < 500) return "General";
  return "General of the Army";
};

const RANK_ORDER = [
  "Private",
  "Private First Class",
  "Corporal",
  "Sergeant",
  "Staff Sergeant",
  "First Sergeant",
  "Master Sergeant",
  "2nd Lieutenant",
  "1st Lieutenant",
  "Captain",
  "Major",
  "Lieutenant Colonel",
  "Colonel",
  "Brigadier General",
  "Major General",
  "Lieutenant General",
  "General",
  "General of the Army",
];

const RANK_ORDER_MAP = RANK_ORDER.reduce((acc, rank, index) => {
  acc[rank] = index;
  return acc;
}, {});

export const sortByRank = (rankA, rankB) => {
  const indexA = RANK_ORDER_MAP[rankA];
  const indexB = RANK_ORDER_MAP[rankB];
  return indexA - indexB;
};

/**
 * Transforms a string to snake case.
 * 'Hello World' -> 'Hello_World'
 * @param {string} str
 * @returns {string}
 */
export const toSnakeCase = (str) => str.replace(/\s+/g, "_");

export const teamToNation = (team) => (team === "axis" ? "ger" : "us");

export function getPlayerTier(level) {
  if (level < 20) {
    return "Novice";
  } else if (level >= 20 && level < 75) {
    return "Apprentice";
  } else if (level >= 75 && level < 200) {
    return "Expert";
  } else if (level >= 200 && level < 350) {
    return "Master";
  } else {
    return "Legend";
  }
}

export function hasRecentWarnings(received_actions) {
  const warningsFrom = dayjs().subtract(1, "day").toISOString();
  const warnings = received_actions.filter(
    (action) => action.time > warningsFrom
  );
  return warnings.length > 0;
}

export const tierColors = {
  Novice: red[500],
  Apprentice: yellow[500],
  Expert: green[500],
  Master: blue[500],
  Legend: purple[500],
};

export const logActions = {
  ADMIN: "🚨",
  "ADMIN MISC": "🚨",
  "ADMIN IDLE": "💤",
  "ADMIN ANTI-CHEAT": "🚷",
  "ADMIN BANNED": "⌛",
  "ADMIN PERMA BANNED": "⛔",
  "ADMIN KICKED": "🚷",
  CHAT: "💬",
  CAMERA: "👀",
  "CHAT[Allies]": "🟦",
  "CHAT[Allies][Team]": "🟦",
  "CHAT[Allies][Unit]": "🟦",
  "CHAT[Axis]": "🟥",
  "CHAT[Axis][Team]": "🟥",
  "CHAT[Axis][Unit]": "🟥",
  CONNECTED: "🛬",
  DISCONNECTED: "🛫",
  KILL: "💀",
  MATCH: "🏁",
  "MATCH ENDED": "🏁",
  "MATCH START": "🏁",
  MESSAGE: "📢",
  "TEAM KILL": "⚠️",
  TEAMSWITCH: "♻️",
  "TK AUTO": "🚷",
  "TK AUTO BANNED": "⌛",
  "TK AUTO KICKED": "🚷",
  VOTE: "🙋",
  "VOTE COMPLETED": "🙋",
  "VOTE EXPIRED": "🙋",
  "VOTE PASSED": "🙋",
  "VOTE STARTED": "🙋",
};

export function getGameDuration(start, end) {
  const totalSeconds = dayjs(end).diff(dayjs(start), 'seconds');
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  // Format the result as hh:mm:ss
  const formattedTime = `${String(hours).padStart(2, '0')}:${String(
    minutes
  ).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

  return formattedTime;
}

export function isLeader(role) {
  return ["officer", "tankcommander", "spotter", "armycommander"].includes(role);
}

export function isSteamPlayer(player) {
  const { player_id: id } = player
  return id.length === 17 && !Number.isNaN(Number(id))
}

export function getSteamProfileUrl(id) {
  return `https://steamcommunity.com/profiles/${id}`
}

export function getXboxProfileUrl(playerName) {
  return `https://xboxgamertag.com/search/${playerName}`
}