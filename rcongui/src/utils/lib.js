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
        if (!match) return { time: "", message: "" };
        const [_, time, content] = match;
        return { time, message: content };
      })
    : [];

export const parseBroadcastMessages = (messages) =>
  messages.reduce((acc, msg, index, arr) => {
    let str = acc + `${msg.time} ${msg.message}`;
    str += index !== arr.length - 1 ? "\n" : "";
    return str;
  }, "");
