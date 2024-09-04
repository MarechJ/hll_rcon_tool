import { Button, FormControl, FormControlLabel, InputLabel, MenuItem, Select, Switch, TextField } from "@mui/material";
import React from "react";
import { get, handle_http_errors, showResponse } from "../../utils/fetchUtils";
import Grid from "@mui/material/Unstable_Grid2";

const BlacklistRecordsSearch = ({
  blacklists,
  onSearch,
  disabled,
}) => {
  const [playerIdQuery, setPlayerIdQuery] = React.useState("");
  const [reasonQuery, setReasonQuery] = React.useState("");
  const [blacklistQuery, setBlacklistQuery] = React.useState("");
  const [excludeExpired, setExcludeExpired] = React.useState(false);
  const [pageSize, setPageSize] = React.useState(50);

  return (
    (<form>
      <Grid
        container
        spacing={2}
        alignContent="center"
        alignItems="center"
        justifyContent="space-evenly"
      >
        <Grid xs={4}>
          <TextField
            fullWidth
            label="Search by player ID"
            value={playerIdQuery}
            onChange={(e) => setPlayerIdQuery(e.target.value)}
          />
        </Grid>
        <Grid xs={8}>
          <TextField
            fullWidth
            label="Search by name or reason"
            value={reasonQuery}
            onChange={(e) => setReasonQuery(e.target.value)}
          />
        </Grid>
        <Grid xs={4}>
          <FormControl fullWidth>
            <InputLabel>Blacklist</InputLabel>
            <Select
              value={blacklistQuery}
              onChange={(e) => setBlacklistQuery(e.target.value)}
            >
              <MenuItem key={""} value={""} style={{minHeight: 36}}>{" "}</MenuItem>
              { blacklists.map(
                (b) => <MenuItem key={b.id} value={b.id}>{b.name}</MenuItem>
              ) }
            </Select>
          </FormControl>
        </Grid>
        <Grid xs={3}>
          <FormControlLabel
            control={
              <Switch
                checked={!excludeExpired}
                onChange={(e) => setExcludeExpired(!e.target.checked)}
                color="primary"
              />
            }
            label="Show Expired"
            labelPlacement="top"
          />
        </Grid>
        <Grid xs={2}>
          <FormControl fullWidth>
            <InputLabel>Page size</InputLabel>
            <Select
              value={pageSize}
              onChange={(e) => setPageSize(e.target.value)}
            >
              <MenuItem value={10}>10</MenuItem>
              <MenuItem value={20}>20</MenuItem>
              <MenuItem value={30}>30</MenuItem>
              <MenuItem value={40}>40</MenuItem>
              <MenuItem value={50}>50</MenuItem>
              <MenuItem value={100}>100</MenuItem>
              <MenuItem value={200}>200</MenuItem>
              <MenuItem value={500}>500</MenuItem>
              <MenuItem value={1000}>1000</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid xs={3}>
          <Button
            type="submit"
            disabled={disabled}
            variant="contained"
            color="primary"
            size="large"
            onClick={(e) => {
              e.preventDefault();
              onSearch({
                player_id: playerIdQuery,
                reason: reasonQuery,
                blacklist_id: blacklistQuery === "" ? null : blacklistQuery,
                exclude_expired: excludeExpired,
                page_size: pageSize,
              });
            }}
          >
            Search
          </Button>
        </Grid>
      </Grid>
    </form>)
  );
}

export default BlacklistRecordsSearch;