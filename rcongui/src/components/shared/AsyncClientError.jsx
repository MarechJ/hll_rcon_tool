import { Alert, AlertTitle, IconButton, Typography } from '@mui/material'
import { useAsyncError } from 'react-router-dom'
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff'
import CloseIcon from '@mui/icons-material/Close'
import { useState } from 'react'

export function AsyncClientError({ title }) {
  const error = useAsyncError()
  const [open, setOpen] = useState(true)

  const handleClose = () => {
    setOpen(false)
  }

  if (!open) return null

  return (
    <Alert
      component={'section'}
      severity={'info'}
      icon={<VisibilityOffIcon fontSize='inherit' />}
      action={
        <IconButton onClick={handleClose}>
          <CloseIcon />
        </IconButton>
      }
    >
      <AlertTitle>{title ?? 'Section'} could not be displayed</AlertTitle>
      <Typography>
        {error?.name} - {error?.message ?? error.statusText}
      </Typography>
    </Alert>
  )
}
