import { List, Typography, Divider } from "@mui/material";
import { MapListItem } from "@/components/MapManager/map-list-item";
import {Fragment} from "react";

export function VoteStatus({ voteStatus, ...props }) {
  return voteStatus.length ? (
    <List dense={true} {...props}>
      {voteStatus.map((mapStatus, index, array) => {
        const { map, voters } = mapStatus;
        return (
          <Fragment key={`${index}#${map.id}`}>
            {index !== 0 && <Divider flexItem variant="inset" />}
            <MapListItem
              mapLayer={map}
              primary={`#${index + 1} ${map.map.pretty_name} -- ${
                voters.length
              } vote${voters.length !== 1 ? "s" : ""}`}
            />
          </Fragment>
        );
      })}
    </List>
  ) : (
    <Typography variant="h4" component={"div"} style={{ padding: 8 }}>
      No VoteMap History
    </Typography>
  );
}
