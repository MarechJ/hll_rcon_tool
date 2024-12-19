import { ControlledTextInput } from '@/components/form/core/ControlledTextInput'

export const DurationField = ({ control, errors, ...props }) => {
  const error = errors['duration']
  const hasError = !!error

  return (
    <ControlledTextInput
      defaultValue={2}
      type={'number'}
      error={hasError}
      name={'duration'}
      label={'Duration'}
      control={control}
      rules={{
        required: 'Duration is required',
        valueAsNumber: true,
        min: { value: 1, message: 'Must be at least 1.' }
      }}
      helperText={hasError ? error.message : 'The duration for the ban in hours.'}
      fullWidth
      {...props}
    />
  )
}
