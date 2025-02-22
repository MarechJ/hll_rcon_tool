import { Stack, Typography, Chip } from "@mui/material";
import dayjs from "dayjs";

const WatchlistList = ({ watchlist }) => {
    if (!watchlist) {
      return <Typography>No watchlist records found</Typography>;
    }
  
    const isActive = watchlist.is_watched;
  
    return (
      <Stack spacing={1}>
        <Typography>{watchlist.reason || "[no reason]"}</Typography>
        <Chip
          label={isActive ? "Active" : "Inactive"}
          color={isActive ? "primary" : "error"}
          variant={isActive ? "filled" : "outlined"}
          sx={{ width: "fit-content" }}
        />
        <Typography>Visits since: {watchlist.count}</Typography>
        <Typography>By: {watchlist.by}</Typography>
        {isActive && (
          <Typography>
            Modified: {dayjs(watchlist.modified).format("LLL")}
          </Typography>
        )}
      </Stack>
    );
  };

export default WatchlistList;
  