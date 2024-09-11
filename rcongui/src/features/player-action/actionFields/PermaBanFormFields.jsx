import { Stack } from '@mui/material'
import { ReasonField } from '../../../components/form/custom/ReasonField'
import { ForwardField } from '../../../components/form/custom/ForwardField';

export const PermaBanFormFields = ({ control, errors }) => {
  return (
    <Stack gap={3}>
      <ForwardField control={control} errors={errors} />
      <ReasonField control={control} errors={errors} />
    </Stack>
  )
};
