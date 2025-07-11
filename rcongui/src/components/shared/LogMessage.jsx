import { PlayerDrawerLink } from "@/components/shared/PlayerDrawerLink";
import { getLogTeam, getTeamColor, removeLogPlayerIds } from "@/utils/lib";
import { Box } from "@mui/material";
import { Fragment } from "react";

export const LogMessage = ({ log, colored = false, short = false, include_ids = false }) => {
  const output = [];
  const teamPlayer1 = getLogTeam(log);
  const teamPlayer2 =
    log.action === "TEAM KILL"
      ? teamPlayer1
      : teamPlayer1 === "Axis"
      ? "Allies"
      : "Axis";
  if (!include_ids || log.action === "MESSAGE") {
    var message = removeLogPlayerIds(log.message);
  } else {
    var message = log.message;
  }
  
  message = message.split(log.player_name_1);
  // In between each element of the array, add the player link
  if (!short) {
    message.forEach((part, index) => {
      if (index % 2 === 0) {
        output.push(
          <Fragment key={index + "a" + "player_id_1"}>{part}</Fragment>
        );
      } else {
        if (log.player_id_1) {
          output.push(
            <PlayerDrawerLink
              playerId={log.player_id_1}
              key={index + "b" + "player_id_1"}
              sx={{ color: colored ? getTeamColor(teamPlayer1) : "inherit" }}
            >
              {log.player_name_1}
            </PlayerDrawerLink>
          );
        } else {
          output.push(
            <Fragment key={index + "b" + "player_id_1"}>
              {log.player_name_1}
            </Fragment>
          );
        }
        output.push(
          <Fragment key={index + "c" + "player_id_1"}>{part}</Fragment>
        );
      }
    });
  }

  if (log.action === "MESSAGE") {
    return <Box sx={{ whiteSpace: "nowrap" }}>{message.join("").slice(2)}</Box>;
  }

  if (message[message.length - 1] && message[message.length - 1] !== "") {
    let messageEnd = message[message.length - 1].split(log.player_name_2);
    output.pop();
    messageEnd.forEach((part, index) => {
      if (index % 2 === 0) {
        if (short) {
          // remove ': ' | '-> ' | '] ' from the start of the string
          part = part?.replace(/^\s*(?::\s|->\s|\]\s)/, "") ?? "";
        }
        output.push(
          <Fragment key={index + "a" + "player_id_2"}>{part}</Fragment>
        );
      } else {
        if (!short && log.player_id_2) {
          output.push(
            <PlayerDrawerLink
              playerId={log.player_id_2}
              key={index + "b" + log.player_id_2}
              sx={{ color: colored ? getTeamColor(teamPlayer2) : "inherit" }}
            >
              {log.player_name_2}
            </PlayerDrawerLink>
          );
        } else if (!short) {
          output.push(
            <Fragment key={index + "b" + log.player_id_2}>
              {log.player_name_2}
            </Fragment>
          );
        }
        output.push(
          <Fragment key={index + "c" + log.player_id_2}>{part}</Fragment>
        );
      }
    });
  }

  return <Box sx={{ whiteSpace: "nowrap" }}>{output}</Box>;
};
