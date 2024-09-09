import { Stack } from '@mui/material'
import { ReasonField } from '../../form/custom/ReasonField'
import { ForwardField } from '../../form/custom/ForwardField';

export const PermaBanFormFields = ({ control, errors }) => {
  return (
    <Stack gap={3}>
      <ForwardField control={control} errors={errors} />
      <ReasonField control={control} errors={errors} />
    </Stack>
  )
};
