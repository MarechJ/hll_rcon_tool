import { TextField } from "@mui/material";
import { Autocomplete } from "@mui/material";
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
      renderOption={(props, option) => {
        const { key, ...optionProps } = props;
        return (
          <li key={key} {...optionProps}>
            <MapDetail mapLayer={option} />
          </li>
        );
      }}
      {...props}
    />
  );
}
