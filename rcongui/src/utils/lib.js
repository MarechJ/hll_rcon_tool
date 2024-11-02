import { green, grey, purple, red } from "@mui/material/colors";

export const TEMPLATE_CATEGORY = {
  WELCOME: "WELCOME",
  BROADCAST: "BROADCAST",
  MESSAGE: "MESSAGE",
  REASON: "REASON",
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
