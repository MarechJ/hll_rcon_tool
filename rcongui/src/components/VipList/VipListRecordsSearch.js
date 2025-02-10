import { Button, FormControl, FormControlLabel, InputLabel, MenuItem, Select, Switch, TextField } from "@mui/material";
import Grid from "@mui/material/Grid2";
import { useState } from "react";

const VipListRecordsSearch = ({
  vipLists: vipLists,
  onSearch,
  disabled,
}) => {
  const [playerIdQuery, setPlayerIdQuery] = useState("");
  const [descriptionQuery, setDescriptionQuery] = useState("");
  const [vipListQuery, setVipListQuery] = useState("");
  const [excludeExpired, setExcludeExpired] = useState(false);
  const [pageSize, setPageSize] = useState(50);

  return (
    (<form>
      <Grid
        container
        spacing={2}
        alignContent="center"
        alignItems="center"
        justifyContent="space-evenly"
      >
        <Grid size={4}>
          <TextField
            fullWidth
            label="Search by player ID"
            value={playerIdQuery}
            onChange={(e) => setPlayerIdQuery(e.target.value)}
          />
        </Grid>
        <Grid size={8}>
          <TextField
            fullWidth
            label="Search by name or description"
            value={descriptionQuery}
            onChange={(e) => setDescriptionQuery(e.target.value)}
          />
        </Grid>
        <Grid size={4}>
          <FormControl fullWidth>
            <InputLabel>VIP List</InputLabel>
            <Select
              value={vipListQuery}
              onChange={(e) => setVipListQuery(e.target.value)}
            >
              <MenuItem key={""} value={""} style={{ minHeight: 36 }}>{" "}</MenuItem>
              {vipLists.map(
                (b) => <MenuItem key={b.id} value={b.id}>{b.name}</MenuItem>
              )}
            </Select>
          </FormControl>
        </Grid>
        <Grid size={3}>
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
        <Grid size={2}>
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
        <Grid size={3}>
          <Button
            type="submit"
            disabled={disabled}
            variant="contained"
            color="primary"
            size="large"
            onClick={(e) => {
              e.preventDefault();
              // TODO update these?
              onSearch({
                player_id: playerIdQuery,
                vip_list_id: vipListQuery === "" ? null : vipListQuery,
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

export default VipListRecordsSearch;
