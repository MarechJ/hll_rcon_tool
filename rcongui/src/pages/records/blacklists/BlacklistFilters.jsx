import {
  Button,
  FormControl,
  FormControlLabel,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Switch,
  TextField,
} from "@mui/material";
import { useEffect, useState } from "react";
import { DEFAULT_RECORD_FILTERS } from "./queries";

export default function BlacklistFilters({
  filters,
  blacklists,
  disabled,
  onSubmit,
}) {
  const [values, setValues] = useState(filters);

  useEffect(() => setValues(filters), [filters]);

  const update = (field, value) =>
    setValues((current) => ({ ...current, [field]: value }));

  const submit = (event) => {
    event.preventDefault();
    onSubmit({ ...values, page: 1 });
  };

  const reset = () => {
    setValues(DEFAULT_RECORD_FILTERS);
    onSubmit(DEFAULT_RECORD_FILTERS);
  };

  return (
    <Stack component="form" spacing={2} onSubmit={submit}>
      <TextField
        label="Player ID"
        value={values.player_id}
        onChange={(event) => update("player_id", event.target.value)}
        fullWidth
      />
      <TextField
        label="Player name or reason"
        value={values.reason}
        onChange={(event) => update("reason", event.target.value)}
        fullWidth
      />
      <FormControl fullWidth>
        <InputLabel id="blacklist-filter-label">Blacklist</InputLabel>
        <Select
          labelId="blacklist-filter-label"
          label="Blacklist"
          value={values.blacklist_id}
          onChange={(event) => update("blacklist_id", event.target.value)}
        >
          <MenuItem value="">All blacklists</MenuItem>
          {blacklists.map((blacklist) => (
            <MenuItem key={blacklist.id} value={String(blacklist.id)}>
              {blacklist.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <FormControl fullWidth>
        <InputLabel id="blacklist-page-size-label">Page size</InputLabel>
        <Select
          labelId="blacklist-page-size-label"
          label="Page size"
          value={values.page_size}
          onChange={(event) => update("page_size", Number(event.target.value))}
        >
          {[10, 20, 50, 100, 200].map((size) => (
            <MenuItem key={size} value={size}>
              {size}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <FormControlLabel
        control={
          <Switch
            checked={!values.exclude_expired}
            onChange={(event) =>
              update("exclude_expired", !event.target.checked)
            }
          />
        }
        label="Show expired records"
      />
      <Stack spacing={1}>
        <Button
          type="button"
          variant="outlined"
          color="secondary"
          onClick={reset}
          disabled={disabled}
        >
          Reset
        </Button>
        <Button type="submit" variant="contained" disabled={disabled}>
          Search
        </Button>
      </Stack>
    </Stack>
  );
}
