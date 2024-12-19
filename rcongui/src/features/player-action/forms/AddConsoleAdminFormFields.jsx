import { ControlledSelect } from '@/components/form/core/ControlledSelect'
import { Stack } from '@mui/material'
import { useEffect } from 'react'

export const AddConsoleAdminFormFields = ({ contextData, control, setError, contextError }) => {
  useEffect(() => {
    if (contextError) {
      setError('role', { message: contextError.message })
    }
  }, [contextError])

  return (
    <Stack spacing={2}>
      <ControlledSelect
        control={control}
        name='role'
        label='Admin Groups'
        rules={{ required: true }}
        options={contextData?.admin_groups?.map((groupName) => ({
          label: groupName,
          value: groupName
        }))}
      />
    </Stack>
  )
}
