import { ReasonField } from '../fields/ReasonField'
import { DurationField } from '../fields/DurationField';
import { Stack } from '@mui/material'
import { ForwardField } from '../fields/ForwardField';

export const TempBanFormFields = (props) => {
  return (
    <Stack gap={3}>
        <ForwardField {...props} />
        <ReasonField {...props} />
        <DurationField {...props} />
    </Stack>
  )
};
