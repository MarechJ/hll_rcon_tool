import { PlayerDrawerLink } from "@/components/shared/PlayerDrawerLink";
import { getLogTeam, getTeamColor, removeLogPlayerIds } from "@/utils/lib";
import { Box } from "@mui/material";
import { Fragment } from "react";

export const LogMessage = ({ log }) => {
  const output = [];
  const teamPlayer1 = getLogTeam(log);
  const teamPlayer2 =
    log.action === "TEAM KILL"
      ? teamPlayer1
      : teamPlayer1 === "Axis"
      ? "Allies"
      : "Axis";
  let message = removeLogPlayerIds(log.message);

  message = message.split(log.player_name_1);
  // In between each element of the array, add the player link
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
            sx={{ color: getTeamColor(teamPlayer1) }}
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

  if (message[message.length - 1] && message[message.length - 1] !== "") {
    let messageEnd = message[message.length - 1].split(log.player_name_2);
    output.pop();
    messageEnd.forEach((part, index) => {
      if (index % 2 === 0) {
        output.push(
          <Fragment key={index + "a" + "player_id_2"}>{part}</Fragment>
        );
      } else {
        if (log.player_id_2) {
          output.push(
            <PlayerDrawerLink
              playerId={log.player_id_2}
              key={index + "b" + log.player_id_2}
              sx={{ color: getTeamColor(teamPlayer2) }}
            >
              {log.player_name_2}
            </PlayerDrawerLink>
          );
        } else {
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
