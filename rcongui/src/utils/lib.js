export const TEMPLATE_CATEGORY = {
  WELCOME: "WELCOME",
  BROADCAST: "BROADCAST",
  MESSAGE: "MESSAGE",
  REASON: "REASON",
};

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
