import FormControlLabel from '@mui/material/FormControlLabel';
import Checkbox from '@mui/material/Checkbox';
import { Controller } from 'react-hook-form';

export function ControlledCheckbox({
  control,
  name,
  disabled,
  rules,
  defaultValue,
  label,
  ...props
}) {
  return (
    <Controller
      disabled={disabled}
      defaultValue={defaultValue}
      rules={rules}
      name={name}
      control={control}
      render={({ field }) => (
        <FormControlLabel
          control={
            <Checkbox
              onChange={field.onChange} // send value to hook form
              onBlur={field.onBlur} // notify when input is touched/blur
              value={field.value} // input value
              name={field.name} // send down the input name
              inputRef={field.ref} // send input ref, so we can focus on input when error appear
              disabled={field.disabled}
              {...props}
            />
          }
          label={label ?? field.name}
        />
      )}
    />
  );
}
