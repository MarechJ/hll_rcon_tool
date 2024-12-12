import { ControlledCheckbox } from '@/components/form/core/ControlledCheckbox';

export const ForwardField = ({ control, errors, ...props }) => {
  const error = errors['forward'];
  const hasError = !!error;

  return (
    <ControlledCheckbox
      checked={props.defaultValue}
      control={control}
      errors={errors}
      name={'forward'}
      label={'Apply to all servers'}
      {...props}
    />
  );
};
