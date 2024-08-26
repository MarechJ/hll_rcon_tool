import * as React from "react";
import { List } from "@material-ui/core";
import { MapListItem } from "../map-list-item";

export function VoteStatus({ voteStatus, ...props }) {
  return (
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
  );
}
