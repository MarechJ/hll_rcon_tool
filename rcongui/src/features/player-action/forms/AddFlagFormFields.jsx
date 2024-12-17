import { Stack, TextField, useTheme } from '@mui/material'
import { ControlledTextInput } from '@/components/form/core/ControlledTextInput'
import { lazy, Suspense, useEffect } from 'react'
import { Controller } from 'react-hook-form'

const LushEmojiPicker = lazy(() => import('emoji-picker-react'))

export const AddFlagFormFields = ({ control, errors, setValue }) => {
  const theme = useTheme()
  let EmojiStyle = {}

  // It is called 'comment' at the backend but it is really a 'note' for the flag
  const noteError = errors['comment']
  const hasNoteError = !!noteError

  const flagError = errors['flag']
  const hasFlagError = !!flagError

  useEffect(() => {
    import('emoji-picker-react').then((epr) => (EmojiStyle = epr.EmojiStyle))
  }, [])

  return (
    <Stack alignContent={'center'} spacing={2}>
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
          helperText={hasNoteError ? noteError.message : 'Your note for this flag.'}
          sx={{ flexGrow: 1 }}
          defaultValue={''}
        />
      </Stack>
      <Suspense fallback={<div>Loading emoji picker...</div>}>
        <LushEmojiPicker
          width={'100%'}
          emojiStyle={EmojiStyle.TWITTER}
          emojiVersion='15'
          skinTonesDisabled={true}
          theme={theme.palette.mode}
          onEmojiClick={({ emoji }) =>
            setValue('flag', emoji, {
              shouldTouch: true,
              shouldValidate: true
            })
          }
        />
      </Suspense>
    </Stack>
  )
}
