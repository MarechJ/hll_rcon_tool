import { Stack, TextField, useTheme } from '@mui/material';
import { ControlledTextInput } from '../../../components/form/core/ControlledTextInput';
import EmojiPicker from '@emoji-mart/react';
import emojis from '@emoji-mart/data';
import React from 'react';
import { Controller } from 'react-hook-form';

// TODO
// useMediaQuery to display different number of emojis per line
export const AddFlagFormFields = ({ control, errors, setValue, ...props }) => {
  const theme = useTheme();

  // It is called 'comment' at the backend but it is really a 'note' for the flag
  const noteError = errors['comment'];
  const hasNoteError = !!noteError;

  const flagError = errors['flag'];
  const hasFlagError = !!flagError;

  return (
    <Stack alignContent={'center'} spacing={2}>
            <style>
      {`em-emoji-picker {
        width: 100%
      }`}
    </style>
      <Stack direction={'row'} spacing={1}>
        <Controller
          defaultValue={''}
          rules={{ required: 'Flag is required.' }}
          name={'flag'}
          control={control}
          render={({ field }) => (
            <TextField
              onChange={field.onChange} // send value to hook form
              onBlur={field.onBlur} // notify when input is touched/blur
              value={field.value} // input value
              name={field.name} // send down the input name
              inputRef={field.ref} // send input ref, so we can focus on input when error appear
              disabled={true}
              label={'Flag'}
              helperText={hasFlagError && flagError.message}
              error={hasFlagError}
              rows={1}
              sx={{ width: '60px', fontSize: '2rem' }}
            />
          )}
        />
        <ControlledTextInput
          control={control}
          error={hasNoteError}
          rows={1}
          label={'Note'}
          name={'comment'}
          helperText={
            hasNoteError ? noteError.message : 'Your note for this flag.'
          }
          sx={{ flexGrow: 1 }}
          defaultValue={''}
        />
      </Stack>
      <EmojiPicker
        style={{ border: '1px solid red' }}
        dynamicWidth={true}
        perLine={8}
        theme={theme.palette.mode}
        data={emojis}
        onEmojiSelect={(emoji) =>
          setValue('flag', emoji.native, {
            shouldTouch: true,
            shouldValidate: true,
          })
        }
      />
    </Stack>
  );
};
