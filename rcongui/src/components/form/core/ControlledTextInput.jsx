import { TextField } from '@mui/material';
import { Controller } from 'react-hook-form';

export function ControlledTextInput({
  control,
  name,
  disabled,
  rules,
  defaultValue,
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
        <TextField
          onChange={field.onChange} // send value to hook form
          onBlur={field.onBlur} // notify when input is touched/blur
          value={field.value} // input value
          name={field.name} // send down the input name
          inputRef={field.ref} // send input ref, so we can focus on input when error appear
          disabled={field.disabled}
          {...props}
        />
      )}
    />
  );
}
