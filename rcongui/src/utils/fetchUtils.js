import React from "react";
import { json } from "react-router-dom";
import { toast } from "react-toastify";

const CRCON_API = `${process.env.REACT_APP_API_URL}`;
const withCRCON = (path) => `${CRCON_API}${path}`;

function GET_Factory(cmd) {
  return async ({ params } = {}) => {
    let location = cmd;
    let data;

    if (params) {
      location += "?" + new URLSearchParams(params).toString();
    }
    const response = await fetch(withCRCON(location), {
      method: "GET", // *GET, POST, PUT, DELETE, etc.
      mode: "cors", // no-cors, *cors, same-origin
      cache: "default", // *default, no-cache, reload, force-cache, only-if-cached
      credentials: "include", // include, *same-origin, omit
      redirect: "follow", // manual, *follow, error
      referrerPolicy: "origin", // no-referrer, *client
    });

    try {
      data = await response.json();
    } catch (error) {
      throw new NotJSONResponseError("The server did not return JSON.");
    }

    if (!response.ok) {
      switch (response.status) {
        case 401:
          throw new AuthError("You are not authenticated.", cmd);
        case 403:
          throw new PermissionError("You are not authorized.", cmd);
        case 504:
          throw new CRCONServerDownError(
            "There was a problem connection to your CRCON server."
          );
        default:
          throw new UnknownError(data.error, data.command);
      }
    }

    if (data.failed) {
      throw new CommandFailedError(data.error, data.command);
    }

    return data.result;
  };
}

function POST_Factory(cmd) {
  return async ({ params, payload = {} } = {}) => {
    let location = cmd;
    let data;

    if (params) {
      location += "?" + new URLSearchParams(params).toString();
    }
    const response = await fetch(withCRCON(location), {
      method: "POST", // *GET, POST, PUT, DELETE, etc.
      mode: "cors", // no-cors, *cors, same-origin
      cache: "default", // *default, no-cache, reload, force-cache, only-if-cached
      credentials: "include", // include, *same-origin, omit
      headers: {
        "Content-Type": "application/json",
      },
      redirect: "follow", // manual, *follow, error
      referrerPolicy: "origin", // no-referrer, *client
      body: JSON.stringify(payload), // body data type must match "Content-Type" header
    });

    try {
      data = await response.json();
    } catch (error) {
      throw new NotJSONResponseError("The server did not return JSON.");
    }

    if (!response.ok) {
      switch (response.status) {
        case 401:
          throw new AuthError("You are not authenticated.", cmd);
        case 403:
          throw new PermissionError("You are not authorized.", cmd);
        case 504:
          throw new CRCONServerDownError(
            "There was a problem connection to your CRCON server."
          );
        default:
          throw new UnknownError(data.error, data.command);
      }
    }

    if (data.failed) {
      throw new CommandFailedError(data.error, data.command);
    }

    return { result: data.result, arguments: data.arguments };
  };
}

export const cmd = {
  ADD_MESSAGE_TEMPLATE: POST_Factory("add_message_template"),
  EDIT_MESSAGE_TEMPLATE: POST_Factory("edit_message_template"),
  GET_MESSAGE_TEMPLATE: GET_Factory("get_message_templates"),
  DELETE_MESSAGE_TEMPLATE: POST_Factory("delete_message_template"),
  GET_ALL_MESSAGE_TEMPLATES: GET_Factory("get_all_message_templates"),
  GET_MESSAGE_TEMPLATES: GET_Factory("get_message_templates"),
  GET_SERVICES: GET_Factory("get_services"),
  TOGGLE_SERVICE: POST_Factory("do_service"),
  GET_AUTOSETTINGS: GET_Factory("get_auto_settings"),
  SET_AUTOSETTINGS: POST_Factory("set_auto_settings"),
  GET_PROFANITIES: GET_Factory("get_profanities"),
  SET_PROFANITIES: POST_Factory("set_profanities"),
  GET_CONSOLE_ADMINS: GET_Factory("get_admin_ids"),
  ADD_CONSOLE_ADMIN: POST_Factory("add_admin"),
  DELETE_CONSOLE_ADMIN: POST_Factory("remove_admin"),
  GET_CONSOLE_ADMIN_GROUPS: GET_Factory("get_admin_groups"),
  GET_PLAYER: GET_Factory("get_player_profile"),
  GET_VIPS: GET_Factory("get_vip_ids"),
  ADD_VIP: POST_Factory("add_vip"),
  DELETE_VIP: POST_Factory("remove_vip"),
  AUTHENTICATE: POST_Factory("login"),
  IS_AUTHENTICATED: GET_Factory("is_logged_in"),
  GET_WELCOME_MESSAGE: GET_Factory("get_welcome_message"),
  SET_WELCOME_MESSAGE: POST_Factory("set_welcome_message"),
  GET_BROADCAST_MESSAGE: GET_Factory("get_broadcast_message"),
  GET_BROADCAST_CONFIG: GET_Factory("get_auto_broadcasts_config"),
  SET_BROADCAST_CONFIG: POST_Factory("set_auto_broadcasts_config"),
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
  }
}

class PermissionError extends Error {
  constructor(message, command) {
    super(message ?? "You are not authorized.");
    this.command = command;
    this.name = "PermissionError";
    this.status = 403;
  }
}

class CommandFailedError extends Error {
  constructor(message, command) {
    super(message);
    this.command = command;
    this.name = "CommandFailedError";
    this.status = 404;
  }
}

class ConnectionError extends Error {
  constructor(message) {
    super(message);
    this.name = "ConnectionError";
    this.status = 504;
  }
}

class CRCONServerDownError extends Error {
  constructor(message) {
    super(message);
    this.name = "CRCONServerDownError";
    this.status = 504;
  }
}

class NotJSONResponseError extends Error {
  constructor(message) {
    super(message);
    this.name = "NotJSONResponseError";
    this.status = 500;
  }
}

class UnknownError extends Error {
  constructor(message, command) {
    super(message);
    this.command = command;
    this.name = "UnknownError";
    this.status = 400;
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
    console.log(error.name, error.message);
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
