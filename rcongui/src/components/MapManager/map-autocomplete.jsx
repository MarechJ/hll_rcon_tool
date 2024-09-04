import { TextField } from "@material-ui/core";
import { Autocomplete } from "@material-ui/lab";
import { MapDetail } from "./map-details";

export function MapAutocomplete({ options, onChange, ...props }) {
  return (
    <Autocomplete
      multiple
      size="small"
      clearOnEscape
      disableCloseOnSelect
      options={options}
      getOptionLabel={(m) => m.pretty_name}
      isOptionEqualToValue={(option, value) => option.id == value.id}
      onChange={onChange}
      renderInput={(params) => (
        <TextField {...params} variant="outlined" label="Select maps" />
      )}
      renderOption={(option) => (
        <MapDetail mapLayer={option} />
      )}
      {...props}
    />
  );
}
