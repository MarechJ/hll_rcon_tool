import React from 'react';
import dayjs from 'dayjs';
import { ControlledDesktopDateTimePicker } from '../core/ControlledDesktopDateTimePicker';

export const ExpirationField = ({ control, errors, ...props }) => {
  const error = errors['expiration'];
  const hasError = !!error;

  if (hasError && error.type === 'moreThanNow') {
    error.message = 'Must be older then current time.';
  }

  return (
    <ControlledDesktopDateTimePicker
      defaultValue={props.defaultValue ?? dayjs()}
      control={control}
      errors={errors}
      name={'expiration'}
      rules={{ required: 'Expiration date is required.', moreThanNow: 'Date must be more then now.', valueAsDate: true, validate: {
        moreThanNow: (value) => dayjs().isBefore(value),
      } }}
      error={error}
      disablePast
      slotProps={{
        textField: {
          helperText: hasError
            ? error.message
            : 'The date the VIP will expire.',
        },
      }}
    />
  );
};
