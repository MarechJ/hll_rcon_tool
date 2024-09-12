import React from 'react';
import dayjs from 'dayjs';
import { ControlledDesktopDateTimePicker } from '@/components/form/core/ControlledDesktopDateTimePicker';

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
      maxDate={dayjs("3000-01-01T00:00:00+00:00")}
      slotProps={{
        textField: {
          helperText: hasError
            ? error.message
            : 'The date this action will expire.',
        },
      }}
    />
  );
};
