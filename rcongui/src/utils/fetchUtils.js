import React from "react";

import { toast } from "react-toastify";

function LoginError(message) {
  this.message = message;
  this.name = "LoginError";
}

function PermissionError(message, command) {
  this.message = message;
  this.command = command;
  this.name = "PermissionError";
}

function InvalidLogin(message) {
  this.message = message;
  this.name = "InvalidLogin";
}

async function handle_response_status(response) {
  if (response.status === 401) {
    throw new LoginError("You must be logged in!");
  }

  if (response.status === 403) {
    throw new PermissionError(
      "You are not authorized to do this!",
      response.url.slice(response.url.indexOf("/api/") + "/api/".length)
    );
  }

  return response;
}

async function handle_http_errors(error) {
  // TODO: uncomment and limit amount of toasts
  if (error.name === "LoginError") {
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
  const response = await fetch(`${process.env.REACT_APP_API_URL}${path}`, {
    method: "GET", // *GET, POST, PUT, DELETE, etc.
    mode: "cors", // no-cors, *cors, same-origin
    cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
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
    cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
    credentials: "include", // include, *same-origin, omit
    headers: {
      "Content-Type": "application/json",
    },

    redirect: "follow", // manual, *follow, error
    referrerPolicy: "origin", // no-referrer, *client
    body: JSON.stringify(data), // body data type must match "Content-Type" header
  });

  if (url.endsWith("login") && response.status === 401) {
    throw new InvalidLogin("bad login");
  }
  return handle_response_status(response); // parses JSON response into native JavaScript objects
}

async function showResponse(response, command, showSuccess) {
  // TODO: limit the amount of toasts
  // TODO: show message when not allowed due to permissions
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

export {
  postData,
  showResponse,
  get,
  handle_http_errors,
  getSharedMessages,
  PermissionError,
  LoginError,
  sendAction,
  addPlayerToWatchList,
};
