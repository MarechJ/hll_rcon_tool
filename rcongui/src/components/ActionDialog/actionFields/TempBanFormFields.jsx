import React from 'react';
import { ReasonField } from '../../form/custom/ReasonField'
import { DurationField } from '../../form/custom/DurationField';
import { Stack } from '@mui/material'
import { ForwardField } from '../../form/custom/ForwardField';

export const TempBanFormFields = ({ control, errors }) => {
  return (
    <Stack gap={3}>
        <ForwardField control={control} errors={errors} />
        <ReasonField control={control} errors={errors} />
        <DurationField control={control} errors={errors} />
    </Stack>
  )
};
