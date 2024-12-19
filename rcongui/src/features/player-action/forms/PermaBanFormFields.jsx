import { Stack } from '@mui/material'
import { ReasonField } from '../fields/ReasonField'
import { ForwardField } from '../fields/ForwardField'

export const PermaBanFormFields = (props) => {
  return (
    <Stack gap={3}>
      <ForwardField {...props} />
      <ReasonField {...props} />
    </Stack>
  )
}
