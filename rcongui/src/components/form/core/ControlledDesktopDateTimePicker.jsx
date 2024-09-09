import { DesktopDateTimePicker } from '@mui/x-date-pickers/DesktopDateTimePicker';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { Controller } from 'react-hook-form';

export const ControlledDesktopDateTimePicker = ({
  control,
  name,
  disabled,
  rules,
  defaultValue,
  ...props
}) => {
  return (
    <Controller
      disabled={disabled}
      defaultValue={defaultValue}
      rules={rules}
      name={name}
      control={control}
      render={({ field }) => (
        <LocalizationProvider dateAdapter={AdapterDayjs}>
          <DesktopDateTimePicker
            onChange={field.onChange} // send value to hook form
            onBlur={field.onBlur} // notify when input is touched/blur
            value={field.value} // input value
            name={field.name} // send down the input name
            inputRef={field.ref} // send input ref, so we can focus on input when error appear
            disabled={field.disabled}
            format='LLL'
            {...props}
          />
        </LocalizationProvider>
      )}
    />
  );
};
