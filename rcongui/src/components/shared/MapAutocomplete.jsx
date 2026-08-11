import { getMapLayerImageSrc } from "@/pages/settings/maps/objectives/helpers";
import { Autocomplete, Box, TextField } from "@mui/material";

export default function MapAutocomplete({ options, selected, onSelect }) {
  return (
    <Autocomplete
      fullWidth
      options={options}
      getOptionLabel={(option) => option?.pretty_name ?? option?.name ?? ""}
      value={options.find((map) => map.id === selected) || null}
      onChange={(event, newValue) => {
        const newMapId = newValue?.id || "";
        onSelect(newMapId);
      }}
      isOptionEqualToValue={(option, value) => option.id === value.id}
      renderInput={(params) => (
        <TextField {...params} label="Select a map" fullWidth />
      )}
      renderOption={(props, option) => (
        <Box
          component="li"
          sx={{ "& > img": { mr: 2, flexShrink: 0 } }}
          {...props}
        >
          <img
            loading="lazy"
            width="40"
            height="24"
            src={getMapLayerImageSrc(option)}
            alt={option?.pretty_name || option?.name}
            style={{ objectFit: "cover", borderRadius: "2px" }}
          />
          {option?.pretty_name || option?.name}
        </Box>
      )}
    />
  );
}
