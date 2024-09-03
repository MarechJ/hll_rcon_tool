import { TextField } from "@material-ui/core";
import { Autocomplete } from "@material-ui/lab";

export function MapAutocomplete({ options, onChange, ...props }) {
  return (
    <Autocomplete
      multiple
      size="small"
      disableCloseOnSelect
      options={options}
      getOptionLabel={(m) => m.pretty_name}
      isOptionEqualToValue={(option, value) => option.id == value.id}
      onChange={onChange}
      renderInput={(params) => (
        <TextField {...params} variant="outlined" label="Select maps" />
      )}
      {...props}
    />
  );
}
