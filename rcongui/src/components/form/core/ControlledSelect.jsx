import { Select, MenuItem, FormControl, InputLabel, FormHelperText } from '@mui/material';
import { Controller } from 'react-hook-form';

export function ControlledSelect({
  control,
  name,
  label,
  disabled = false,
  rules,
  defaultValue = '',
  options = [],
  ...props
}) {
  return (
    <FormControl fullWidth disabled={disabled}>
      <InputLabel>{label}</InputLabel>
      <Controller
        name={name}
        control={control}
        defaultValue={defaultValue}
        rules={rules}
        render={({ field, fieldState: { error } }) => (
          <>
            <Select
              label={label}
              value={field.value || ''} // use empty string as fallback for value
              onChange={field.onChange}
              onBlur={field.onBlur}
              inputRef={field.ref}
              disabled={disabled}
              error={!!error}
              {...props}
          >
            {options.map((option) => (
              <MenuItem key={option.value} value={option.value}>
                {option.label}
              </MenuItem>
            ))}
          </Select>
            {error && <FormHelperText>{error?.message ?? error?.text ?? "Error"}</FormHelperText>}
          </>
        )}
      />
    </FormControl>
  );
}
