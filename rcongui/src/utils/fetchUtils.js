import React from 'react'

import { toast } from "react-toastify";


function LoginError(message) {
  this.message = message;
  this.name = 'LoginError';
}

function PermissionError(message) {
  this.message = message;
  this.name = 'PermissionError';
}

function InvalidLogin(message) {
  this.message = message;
  this.name = 'InvalidLogin';
}

async function handle_response_status(response) {
  if (response.status === 401) {
    throw new LoginError("You must be logged in!")
  }

  if (response.status === 403) {
    throw new PermissionError("You are not authorized to do this!")
  }
  return response
}


async function handle_http_errors(error) {
  // TODO: uncomment and limit amount of toasts
  if (error.name === 'LoginError') {
    toast.warn("Please login!", {
      toastId: "Must login",
      position: toast.POSITION.BOTTOM_RIGHT,
    })
  }
  else if (error.name == 'PermissionError') {
    toast.warn("You are not allowed to do this", {
      toastId: "Not allowed",
    })
  } else if (error.name == 'InvalidLogin') {
    toast.warn(<img src="https://media.giphy.com/media/wSSooF0fJM97W/giphy.gif"/>, {
      toastId: "Bad loging",
    })
  } else {
    toast.error("Unable to connect to API " + error)
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

  return handle_response_status(response)
}

async function postData(url = "", data = {}) {
  // Default options are marked with *
  const response = await fetch(url, {
    method: "POST", // *GET, POST, PUT, DELETE, etc.
    mode: "cors", // no-cors, *cors, same-origin
    cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
    credentials: "include", // include, *same-origin, omit
    headers: {
      "Content-Type": "application/json"
    },

    redirect: "follow", // manual, *follow, error
    referrerPolicy: "origin", // no-referrer, *client
    body: JSON.stringify(data) // body data type must match "Content-Type" header
  });

  if (url.endsWith('login') && response.status === 401) {
    throw new InvalidLogin("bad login")
  }
  return handle_response_status(response); // parses JSON response into native JavaScript objects
}

async function showResponse(response, command, showSuccess) {
  // TODO: limit the amount of toasts
  if (!response.ok) {
    toast.error(`Game server failed to return for ${command}`);
  } else {
    const res = await response.json();
    if (res.failed === true) {
      toast.warning(`Last command failed: ${command} -> ${JSON.stringify(res.result)}\n\nError: ${res.error}`);
    } else if (showSuccess === true) {
      toast.success(`Done: ${command}`);
    }
    return res;
  }
  return response.json();
}

async function sendAction(command, parameters) {
  return postData(`${process.env.REACT_APP_API_URL}${command}`, parameters).then(
    (res) => showResponse(res, command, true)
  ).catch(handle_http_errors)
} 

async function _checkResult(data) {
  if (data.result) {
    return data.result
  }
  return []
}

async function getSharedMessages(namespace) {
  return get(`get_standard_messages?message_type=${namespace}`)
  .then((res) => res.json()).then(_checkResult)
}

export { postData, showResponse, get, handle_http_errors, getSharedMessages, PermissionError, LoginError, sendAction };




