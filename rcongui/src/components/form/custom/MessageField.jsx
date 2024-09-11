import { ControlledTextInput } from "../core/ControlledTextInput";

export const MessageField = ({ control, errors, ...props }) => {
  const error = errors['message'];
  const hasError = !!error;

  return (
    <ControlledTextInput
      error={hasError}
      name={'message'}
      label={'Message'}
      control={control}
      rules={{ required: 'Message is required' }}
      helperText={hasError ? error.message : 'The message displayed to the player.'}
      multiline
      minRows={5}
      fullWidth
      {...props}
    />
  );
};
