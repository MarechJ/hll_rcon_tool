import { json } from "react-router-dom";
import { toast } from "react-toastify";

const CRCON_API = `${process.env.REACT_APP_API_URL}`;
const usingCRCON = (path) => `${CRCON_API}${path}`;

async function requestFactory({
  method = "GET",
  cmd,
  params = {},
  payload = {},
  throwRouteError = true,
  headers = { "Content-Type": "application/json" },
} = {}) {
  let url = cmd;

  if (params) {
    if (params instanceof URLSearchParams) {
      url += "?" + params.toString();
    } else if (method === "GET") {
      url += "?" + new URLSearchParams(params).toString();
    }
  }

  const body = method === "POST" ? headers["Content-Type"] === "application/json" ? JSON.stringify(payload) : payload : null;

  try {
    const response = await fetch(usingCRCON(url), {
      method,
      mode: "cors",
      cache: "default",
      credentials: "include",
      headers,
      redirect: "follow",
      referrerPolicy: "origin",
      body,
    });

    return await handleFetchResponse(response, method);
  } catch (error) {
    if (throwRouteError) {
      throw json(error, { status: error.status, statusText: error.message || error.text });
    }
    throw error;
  }
}

async function handleFetchResponse(response, method) {
  let data;

  const contentType = response.headers.get("content-type");
  if (contentType && contentType.includes("application/json")) {
    data = await parseJsonResponse(response);
  } else if (contentType && contentType.includes("text/plain")) {
    data = await response.text();
  }

  handleServerErrors(response, data);
  handleClientErrors(response, data);

  if (contentType && contentType.includes("text/plain")) {
    return data;
  }

  if (method === "GET") {
    return data.result
  } else if (method === "POST") {
    return data;
  }
  return data;
}

function handleServerErrors(response, data) {
  if (!response.ok && response.status >= 500) {
    switch (response.status) {
      case 504:
        throw new CRCONServerDownError("There was a problem connecting to your CRCON server.");
      default:
        if (data) throw new UnknownError(data.error, data.command);
        throw new UnknownError(response.statusText, response.status);
    }
  }
}

function handleClientErrors(response, data) {
  if (!response.ok) {
    switch (response.status) {
      case 401:
        throw new AuthError("You are not authenticated.", data.command);
      case 403:
        throw new PermissionError("You are not authorized.", data.command);
      default:
        throw new UnknownError(data.error, data.command);
    }
  }
  if (data.failed) {
    throw new CommandFailedError(data.error, data.command);
  }
}

async function parseJsonResponse(response) {
  try {
    return await response.json();
  } catch {
    throw new NotJSONResponseError("The server did not return valid JSON.");
  }
}

export const cmd = {
  ADD_CONSOLE_ADMIN: (params) => requestFactory({ method: "POST", cmd: "add_admin", ...params }),
  ADD_MESSAGE_TEMPLATE: (params) => requestFactory({ method: "POST", cmd: "add_message_template", ...params }),
  ADD_VIP: (params) => requestFactory({ method: "POST", cmd: "add_vip", ...params }),
  AUTHENTICATE: (params) => requestFactory({ method: "POST", cmd: "login", ...params }),
  CLEAR_APPLICATION_CACHE: (params) => requestFactory({ method: "POST", cmd: "clear_cache", ...params }),
  DELETE_CONSOLE_ADMIN: (params) => requestFactory({ method: "POST", cmd: "remove_admin", ...params }),
  DELETE_MESSAGE_TEMPLATE: (params) => requestFactory({ method: "POST", cmd: "delete_message_template", ...params }),
  DELETE_VIP: (params) => requestFactory({ method: "POST", cmd: "remove_vip", ...params }),
  EDIT_MESSAGE_TEMPLATE: (params) => requestFactory({ method: "POST", cmd: "edit_message_template", ...params }),
  FLAG_PLAYER: (params) => requestFactory({ method: "POST", cmd: "flag_player", ...params }),
  GET_AUDIT_LOGS: (params) => requestFactory({ method: "GET", cmd: "get_audit_logs", ...params }),
  GET_AUDIT_LOGS_AUTOCOMPLETE: (params) => requestFactory({ method: "GET", cmd: "get_audit_logs_autocomplete", ...params }),
  GET_ALL_MESSAGE_TEMPLATES: (params) => requestFactory({ method: "GET", cmd: "get_all_message_templates", ...params }),
  GET_AUTOSETTINGS: (params) => requestFactory({ method: "GET", cmd: "get_auto_settings", ...params }),
  GET_BANS: (params) => requestFactory({ method: "GET", cmd: "get_bans", ...params }),
  GET_BLACKLISTS: (params) => requestFactory({ method: "GET", cmd: "get_blacklists", ...params }),
  GET_BROADCAST_CONFIG: (params) => requestFactory({ method: "GET", cmd: "get_auto_broadcasts_config", ...params }),
  GET_BROADCAST_MESSAGE: (params) => requestFactory({ method: "GET", cmd: "get_broadcast_message", ...params }),
  GET_CAMERA_NOTIFICATION_CONFIG: (params) => requestFactory({ method: "GET", cmd: "get_camera_notification_config", ...params }),
  GET_COMPLETED_GAME_DETAIL: (params) => requestFactory({ method: "GET", cmd: "get_map_scoreboard", ...params }),
  GET_COMPLETED_GAMES: (params) => requestFactory({ method: "GET", cmd: "get_scoreboard_maps", ...params }),
  GET_CONSOLE_ADMIN_GROUPS: (params) => requestFactory({ method: "GET", cmd: "get_admin_groups", ...params }),
  GET_CONSOLE_ADMINS: (params) => requestFactory({ method: "GET", cmd: "get_admin_ids", ...params }),
  GET_CRCON_MODS: (params) => requestFactory({ method: "GET", cmd: "get_online_mods", ...params }),
  GET_CRCON_SERVER_CONNECTION: (params) => requestFactory({ method: "GET", cmd: "get_connection_info", ...params }),
  GET_GAME_SERVER_LIST: (params) => requestFactory({ method: "GET", cmd: "get_server_list", ...params }),
  GET_GAME_SERVER_STATUS: (params) => requestFactory({ method: "GET", cmd: "get_status", ...params }),
  GET_GAME_STATE: (params) => requestFactory({ method: "GET", cmd: "get_gamestate", ...params }),
  // Yes, it is POST request, but it is not a POST command => it's not mutating the server state
  GET_HISTORICAL_LOGS: (params) => requestFactory({ method: "POST", cmd: "get_historical_logs", ...params }),
  GET_INGAME_MODS: (params) => requestFactory({ method: "GET", cmd: "get_ingame_mods", ...params }),
  GET_LIVE_GAME: (params) => requestFactory({ method: "GET", cmd: "get_live_game_stats", ...params }),
  // Yes, it is POST request, but it is not a POST command => it's not mutating the server state
  GET_LIVE_LOGS: (params) => requestFactory({ method: "POST", cmd: "get_recent_logs", ...params }),
  GET_LIVE_SESSIONS: (params) => requestFactory({ method: "GET", cmd: "get_live_scoreboard", ...params }),
  GET_LIVE_TEAMS: (params) => requestFactory({ method: "GET", cmd: "get_team_view", ...params }),
  GET_MAP_ROTATION: (params) => requestFactory({ method: "GET", cmd: "get_map_rotation", ...params }),
  GET_MESSAGE_TEMPLATE: (params) => requestFactory({ method: "GET", cmd: "get_message_template", ...params }),
  GET_MESSAGE_TEMPLATES: (params) => requestFactory({ method: "GET", cmd: "get_message_templates", ...params }),
  GET_SEEDING_CONFIG: (params) => requestFactory({ method: "GET", cmd: "get_auto_mod_seeding_config", ...params }),
  GET_NO_LEADER_CONFIG: (params) => requestFactory({ method: "GET", cmd: "get_auto_mod_no_leader_config", ...params }),
  GET_NO_SOLO_TANK_CONFIG: (params) => requestFactory({ method: "GET", cmd: "get_auto_mod_solo_tank_config", ...params }),
  GET_LEVEL_CONFIG: (params) => requestFactory({ method: "GET", cmd: "get_auto_mod_level_config", ...params }),
  GET_NAME_KICKS_CONFIG: (params) => requestFactory({ method: "GET", cmd: "get_name_kick_config", ...params }),
  GET_VAC_CONFIG: (params) => requestFactory({ method: "GET", cmd: "get_vac_game_bans_config", ...params }),
  GET_SEEDING_REWARD_CONFIG: (params) => requestFactory({ method: "GET", cmd: "get_seed_vip_config", ...params }),
  GET_CHAT_COMMANDS_CONFIG: (params) => requestFactory({ method: "GET", cmd: "get_chat_commands_config", ...params }),
  GET_RCON_CHAT_COMMANDS_CONFIG: (params) => requestFactory({ method: "GET", cmd: "get_rcon_chat_commands_config", ...params }),
  GET_ONLINE_PLAYERS: (params) => requestFactory({ method: "GET", cmd: "get_players", ...params }),
  GET_PERMISSIONS: (params) => requestFactory({ method: "GET", cmd: "get_own_user_permissions", ...params }),
  GET_PLAYER: (params) => requestFactory({ method: "GET", cmd: "get_player_profile", ...params }),
  GET_PLAYER_BANS: (params) => requestFactory({ method: "GET", cmd: "get_ban", ...params }),
  GET_PLAYER_COMMENTS: (params) => requestFactory({ method: "GET", cmd: "get_player_comments", ...params }),
  GET_PLAYER_MESSAGES: (params) => requestFactory({ method: "GET", cmd: "get_player_messages", ...params }),
  // Yes, it is POST request, but it is not a POST command => it's not mutating the server state
  GET_PLAYERS_RECORDS: (params) => requestFactory({ method: "POST", cmd: "get_players_history", ...params }),
  GET_PROFANITIES: (params) => requestFactory({ method: "GET", cmd: "get_profanities", ...params }),
  GET_PUBLIC_GAME_STATE: (params) => requestFactory({ method: "GET", cmd: "get_public_info", ...params }),
  GET_REAL_VIP_CONFIG: (params) => requestFactory({ method: "GET", cmd: "get_real_vip_config", ...params }),
  GET_SERVER_NAME: (params) => requestFactory({ method: "GET", cmd: "get_name", ...params }),
  GET_SERVER_SETTINGS: (params) => requestFactory({ method: "GET", cmd: "get_server_settings", ...params }),
  GET_SERVICES: (params) => requestFactory({ method: "GET", cmd: "get_services", ...params }),
  GET_VERSION: (params) => requestFactory({ method: "GET", cmd: "get_version", ...params }),
  GET_VIPS: (params) => requestFactory({ method: "GET", cmd: "get_vip_ids", ...params }),
  GET_VOTEKICK_AUTOTOGGLE_CONFIG: (params) => requestFactory({ method: "GET", cmd: "get_votekick_autotoggle_config", ...params }),
  GET_WELCOME_MESSAGE: (params) => requestFactory({ method: "GET", cmd: "get_welcome_message", ...params }),
  IS_AUTHENTICATED: (params) => requestFactory({ method: "GET", cmd: "is_logged_in", ...params }),
  LOGOUT: (params) => requestFactory({ method: "GET", cmd: "logout", ...params }),
  RECONNECT_GAME_SERVER: (params) => requestFactory({ method: "POST", cmd: "reconnect_gameserver", ...params }),
  RESET_VOTEKICK_THRESHOLDS: (params) => requestFactory({ method: "POST", cmd: "reset_votekick_thresholds", ...params }),
  SET_AUTOBALANCE_ENABLED: (params) => requestFactory({ method: "POST", cmd: "set_autobalance_enabled", ...params }),
  SET_AUTOBALANCE_THRESHOLD: (params) => requestFactory({ method: "POST", cmd: "set_autobalance_threshold", ...params }),
  SET_AUTOSETTINGS: (params) => requestFactory({ method: "POST", cmd: "set_auto_settings", ...params }),
  SET_BROADCAST_CONFIG: (params) => requestFactory({ method: "POST", cmd: "set_auto_broadcasts_config", ...params }),
  SET_CAMERA_NOTIFICATION_CONFIG: (params) => requestFactory({ method: "POST", cmd: "set_camera_notification_config", ...params }),
  SET_IDLE_AUTOKICK_TIME: (params) => requestFactory({ method: "POST", cmd: "set_idle_autokick_time", ...params }),
  SET_MAX_PING_AUTOKICK: (params) => requestFactory({ method: "POST", cmd: "set_max_ping_autokick", ...params }),
  SET_PROFANITIES: (params) => requestFactory({ method: "POST", cmd: "set_profanities", ...params }),
  SET_QUEUE_LENGTH: (params) => requestFactory({ method: "POST", cmd: "set_queue_length", ...params }),
  SET_REAL_VIP_CONFIG: (params) => requestFactory({ method: "POST", cmd: "set_real_vip_config", ...params }),
  SET_SERVER_NAME: (params) => requestFactory({ method: "POST", cmd: "set_server_name", ...params }),
  SET_TEAM_SWITCH_COOLDOWN: (params) => requestFactory({ method: "POST", cmd: "set_team_switch_cooldown", ...params }),
  SET_VIP_SLOTS_NUM: (params) => requestFactory({ method: "POST", cmd: "set_vip_slots_num", ...params }),
  SET_VOTEKICK_AUTOTOGGLE_CONFIG: (params) => requestFactory({ method: "POST", cmd: "set_votekick_autotoggle_config", ...params }),
  SET_VOTEKICK_ENABLED: (params) => requestFactory({ method: "POST", cmd: "set_votekick_enabled", ...params }),
  SET_VOTEKICK_THRESHOLDS: (params) => requestFactory({ method: "POST", cmd: "set_votekick_thresholds", ...params }),
  SET_WELCOME_MESSAGE: (params) => requestFactory({ method: "POST", cmd: "set_welcome_message", ...params }),
  TOGGLE_SERVICE: (params) => requestFactory({ method: "POST", cmd: "do_service", ...params }),
  UNFLAG_PLAYER: (params) => requestFactory({ method: "POST", cmd: "unflag_player", ...params }),
  // Files
  DOWNLOAD_VIP_FILE: (params) => requestFactory({ method: "GET", cmd: "download_vips", ...params }),
  UPLOAD_VIP_FILE: (params) => requestFactory({ method: "POST", cmd: "upload_vips", ...params }),
  GET_UPLOAD_VIP_FILE_RESPONSE: (params) => requestFactory({ method: "GET", cmd: "upload_vips_result", ...params }),
};

export function execute(command, data) {
  return postData(CRCON_API + command, data);
}

// used for React Router loaders
export function handleHttpError(error) {
  let errorObject, init;

  switch (error.name) {
    case "PermissionError":
      errorObject = {
        message: "You don't have permissions to do that!",
        error: error?.name,
        command: error?.command,
      };
      init = { status: 403 };
      break;
    case "AuthError":
      errorObject = {
        message: "You are not authenticated!",
        error: error?.name,
        command: error?.command,
      };
      init = { status: 401 };
      break;
    case "CommandFailedError":
      errorObject = {
        message: error?.message,
        error: error?.name,
        command: error?.command,
      };
      init = { status: 404 };
      break;
    case "CRCONServerDownError":
      errorObject = {
        message: error?.message,
        error: error?.name,
        command: error?.command,
      };
      init = { status: 504 };
      break;
    default:
      errorObject = {
        message: error?.message ?? "Something went wrong",
        error: error?.name,
        command: error?.command,
      };
      init = { status: 400 };
      break;
  }

  throw json(errorObject, init);
}

class AuthError extends Error {
  constructor(message) {
    super(message ?? "You are not authenticated.");
    this.name = "AuthError";
    this.status = 401;
    this.text = message;
  }
}

class PermissionError extends Error {
  constructor(message, command) {
    super(message ?? "You are not authorized.");
    this.command = command;
    this.name = "PermissionError";
    this.status = 403;
    this.text = message;
  }
}

class CommandFailedError extends Error {
  constructor(message, command) {
    super(message);
    this.command = command;
    this.name = "CommandFailedError";
    this.text = message;
    this.status = 404;
  }
}

class ConnectionError extends Error {
  constructor(message) {
    super(message);
    this.name = "ConnectionError";
    this.status = 504;
    this.text = message;
  }
}

class CRCONServerDownError extends Error {
  constructor(message) {
    super(message);
    this.name = "CRCONServerDownError";
    this.status = 504;
    this.text = message;
  }
}

class NotJSONResponseError extends Error {
  constructor(message) {
    super(message);
    this.name = "NotJSONResponseError";
    this.status = 500;
    this.text = message;
  }
}

class UnknownError extends Error {
  constructor(message, command, status) {
    super(message);
    this.command = command;
    this.name = "UnknownError";
    this.status = status ?? 400;
    this.text = message;
  }
}

async function handle_response_status(response) {
  if (response.status === 401) {
    throw new AuthError("You must be logged in!");
  }

  if (response.status === 403) {
    throw new PermissionError(
      "You are not authorized to do this!",
      response.url.slice(response.url.indexOf("/api/") + "/api/".length)
    );
  }

  if (response.status === 504) {
    throw new CRCONServerDownError(
      response.statusText + ". Your server is not responding."
    );
  }

  return response;
}

async function handle_http_errors(error) {
  // TODO: uncomment and limit amount of toasts
  if (error.name === "AuthError") {
    toast.warn("Please login!", {
      toastId: "Must login",
      position: toast.POSITION.BOTTOM_RIGHT,
    });
  } else if (error.name === "PermissionError") {
    toast.warn(`You are not allowed to use ${error.command}`, {
      toastId: "Not allowed",
    });
  } else if (error.name === "InvalidLogin") {
    toast.warn(
      <img
        src="https://media.giphy.com/media/wSSooF0fJM97W/giphy.gif"
        alt="bad login"
      />,
      {
        toastId: "Bad login",
      }
    );
  } else if (error.name === "TypeError" || error.name === "SyntaxError") {
    toast.error(
      "Your RCON Api is not reachable. Check your config and start it again",
      {
        toastId: "Api down",
      }
    );
  } else {
    toast.error("Unable to connect to API " + error);
  }
}

async function get(path) {
  const response = await fetch(`${CRCON_API}${path}`, {
    method: "GET", // *GET, POST, PUT, DELETE, etc.
    mode: "cors", // no-cors, *cors, same-origin
    cache: "default", // *default, no-cache, reload, force-cache, only-if-cached
    credentials: "include", // include, *same-origin, omit
    redirect: "follow", // manual, *follow, error
    referrerPolicy: "origin", // no-referrer, *client
  });

  return handle_response_status(response);
}

async function postData(url = "", data = {}) {
  // Default options are marked with *
  const response = await fetch(url, {
    method: "POST", // *GET, POST, PUT, DELETE, etc.
    mode: "cors", // no-cors, *cors, same-origin
    cache: "default", // *default, no-cache, reload, force-cache, only-if-cached
    credentials: "include", // include, *same-origin, omit
    headers: {
      "Content-Type": "application/json",
    },
    redirect: "follow", // manual, *follow, error
    referrerPolicy: "origin", // no-referrer, *client
    body: JSON.stringify(data), // body data type must match "Content-Type" header
  });

  return handle_response_status(response); // parses JSON response into native JavaScript objects
}

async function showResponse(response, command, showSuccess) {
  if (!response.ok) {
    toast.error(`Game server failed to return for ${command}`, {
      toastId: "connectionError",
    });
  } else {
    const res = await response.json();
    if (res.failed === true) {
      toast.warning(
        `Last command failed: ${command} -> ${JSON.stringify(
          res.result
        )}\n\nError: ${res.error}`
      );
      return res;
    } else if (showSuccess === true) {
      toast.success(`Done: ${command}`);
    }
    try {
      if (res.forward_results) {
        res.forward_results.forEach((r) => {
          if (r.response.failed === true) {
            toast.warning(`${r.host} Last command failed: ${command}`);
          } else if (r.response.failed === false && showSuccess === true) {
            toast.success(`${r.host} Done: ${command}`);
          }
        });
      }
    } catch (error) {
      console.log("Error checking forwards status", error);
    }

    return res;
  }
  return response.json();
}

async function sendAction(command, parameters) {
  return postData(`${process.env.REACT_APP_API_URL}${command}`, parameters)
    .then((res) => showResponse(res, command, true))
    .catch(handle_http_errors);
}

async function _checkResult(data) {
  if (data.result) {
    let unescaped = data.result.messages.map((ele) =>
      ele.replaceAll(/\\n/g, "\n")
    );
    unescaped = unescaped.map((ele) => ele.replaceAll(/\\t/g, "\t"));
    return unescaped;
  }
  return [];
}

async function getSharedMessages(namespace) {
  return get(`get_standard_${namespace}_messages`)
    .then((res) => res.json())
    .then((res) => {
      return res;
    })
    .then(_checkResult);
}

async function addPlayerToWatchList(player_id, reason, playerName) {
  return postData(`${process.env.REACT_APP_API_URL}watch_player`, {
    player_id: player_id,
    reason: reason,
    player_name: playerName,
  })
    .then((response) =>
      showResponse(response, `Player ID ${player_id} watched`, true)
    )
    .catch(handle_http_errors);
}

async function addPlayerToBlacklist({
  blacklistId,
  playerId,
  expiresAt,
  reason,
}) {
  try {
    const response = await postData(
      `${process.env.REACT_APP_API_URL}add_blacklist_record`,
      {
        blacklist_id: blacklistId,
        player_id: playerId,
        expires_at: expiresAt || null,
        reason,
      }
    );

    return showResponse(
      response,
      `Player ID ${playerId} was blacklisted`,
      true
    );
  } catch (error) {
    handle_http_errors(error);
  }
}

async function getBlacklists() {
  try {
    const response = await get("get_blacklists");
    const data = await showResponse(response, "get_blacklists", false);
    if (data.result) {
      return data.result;
    }
  } catch (error) {
    handle_http_errors(error);
  }
}

async function getServerStatus() {
  try {
    const response = await get("get_status");
    const data = await response.json();
    if (data.result) {
      return data.result;
    }
  } catch (error) {
    handle_http_errors(error);
  }
}

async function getGameState() {
  try {
    const response = await get("get_gamestate");
    const data = await response.json();
    if (data.result) {
      return data.result;
    }
  } catch (error) {
    handle_http_errors(error);
  }
}

async function getVips() {
  try {
    const response = await get("get_vip_ids");
    const data = await response.json();
    if (data.result) {
      return data.result;
    }
  } catch (error) {
    handle_http_errors(error);
  }
}

async function addPlayerVip(player) {
  try {
    const response = await execute("add_vip", player);
    const data = await showResponse(response, "add_vip", true);
    if (data.result) {
      return data.result;
    }
  } catch (error) {
    handle_http_errors(error);
  }
}

async function removePlayerVip(player) {
  try {
    const response = await execute("remove_vip", player);
    const data = await showResponse(response, "remove_vip", true);
    if (data.result) {
      return data.result;
    }
  } catch (error) {
    handle_http_errors(error);
  }
}

async function resetVotemapState() {
  try {
    const response = await execute("reset_votemap_state");
    const data = await showResponse(response, "reset_votemap_state", true);
    if (data.result) {
      return data.result;
    }
  } catch (error) {
    handle_http_errors(error);
  }
}

async function updateVotemapConfig(config) {
  try {
    const response = await execute("set_votemap_config", config);
    const data = await showResponse(response, "set_votemap_config", true);
    if (data.result) {
      return data.result;
    }
  } catch (error) {
    handle_http_errors(error);
  }
}

async function getVotemapStatus() {
  try {
    const response = await get("get_votemap_status");
    const data = await response.json();
    if (data.result) {
      return data.result;
    }
  } catch (error) {
    handle_http_errors(error);
  }
}

async function getVotemapConfig() {
  try {
    const response = await get("get_votemap_config");
    const data = await response.json();
    if (data.result) {
      return data.result;
    }
  } catch (error) {
    handle_http_errors(error);
  }
}

async function changeMap(mapId) {
  try {
    const response = await execute("set_map", { map_name: mapId });
    const data = await showResponse(response, `Map changed to ${mapId}`, true);
    if (data.result) {
      return data.result;
    }
  } catch (error) {
    handle_http_errors(error);
  }
}

async function changeGameLayout(payload) {
  try {
    const response = await execute("set_game_layout", payload);
    const data = await showResponse(response, "set_game_layout", true);
    if (data.result) {
      return data.result;
    }
  } catch (error) {
    handle_http_errors(error);
  }
}

async function getMapObjectives() {
  try {
    const response = await get("get_objective_rows");
    const data = await response.json();
    if (data.result) {
      return data.result;
    }
  } catch (error) {
    handle_http_errors(error);
  }
}

async function getVotemapWhitelist() {
  try {
    const response = await get("get_votemap_whitelist");
    const data = await response.json();
    if (data.result) {
      return data.result;
    }
  } catch (error) {
    handle_http_errors(error);
  }
}

async function setVotemapWhitelist(payload) {
  try {
    const response = await execute("set_votemap_whitelist", {
      map_names: payload,
    });
    const data = await showResponse(response, "set_votemap_whitelist", true);
    if (data) {
      return data?.arguments?.map_names;
    }
  } catch (error) {
    handle_http_errors(error);
  }
}

async function resetVotemapWhitelist() {
  try {
    const response = await execute("reset_map_votemap_whitelist", {});
    const data = await showResponse(
      response,
      "reset_map_votemap_whitelist",
      true
    );
    if (data.result) {
      return data.result;
    }
  } catch (error) {
    handle_http_errors(error);
  }
}

export {
  postData,
  showResponse,
  get,
  handle_http_errors,
  getSharedMessages,
  PermissionError,
  AuthError,
  sendAction,
  addPlayerToWatchList,
  addPlayerToBlacklist,
  getBlacklists,
  getServerStatus,
  addPlayerVip,
  removePlayerVip,
  getVips,
  resetVotemapState,
  getVotemapStatus,
  getVotemapConfig,
  updateVotemapConfig,
  changeMap,
  changeGameLayout,
  getMapObjectives,
  getGameState,
  getVotemapWhitelist,
  setVotemapWhitelist,
  resetVotemapWhitelist,
};
