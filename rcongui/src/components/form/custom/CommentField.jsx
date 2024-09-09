import { ControlledTextInput } from "../core/ControlledTextInput";

export const CommentField = ({ control, errors, ...props }) => {
  const error = errors['comment'];
  const hasError = !!error;

  return (
    <ControlledTextInput
      error={hasError}
      name={'comment'}
      label={'Comment'}
      control={control}
      rules={{ minLength: { value: 5, message: 'Must be at least 5 characters long.' }, ...props.rules }}
      helperText={hasError ? error.message : 'The comment saved to the player profile.'}
      multiline
      minRows={5}
      fullWidth
      {...props}
    />
  );
};
