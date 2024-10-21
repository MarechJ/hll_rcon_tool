import * as React from "react";
import { List, Typography } from "@mui/material";
import { MapListItem } from "@/components/MapManager/map-list-item";

export function VoteStatus({ voteStatus, ...props }) {
  return voteStatus.length ? (
    <List dense={true} {...props}>
      {voteStatus.map((mapStatus, index) => {
        const { map, voters } = mapStatus;
        return (
          <MapListItem
            key={`${index}#${map.id}`}
            mapLayer={map}
            primary={`#${index + 1} ${map.map.pretty_name} -- ${
              voters.length
            } vote${voters.length !== 1 ? "s" : ""}`}
          />
        );
      })}
    </List>
  ) : (
    <Typography variant="h4" component={"div"} style={{ padding: 8 }}>No VoteMap History</Typography>
  );
}
