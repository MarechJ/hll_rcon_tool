import { parseBroadcastMessages } from '@/utils/lib'
import { Box, Button, IconButton, Stack, styled, TextField } from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import DeleteIcon from '@mui/icons-material/Delete'

const StyledTextField = styled(TextField)((theme) => ({
  '& .MuiOutlinedInput-root, & .MuiOutlinedInput-notchedOutline': {
    borderRadius: 0
  }
}))

export function BroadcastFields({ messages, disabled, onChange, ...props }) {
  const handleAddRow = () => {
    onChange([...messages, { time_sec: '', message: '' }])
  }

  const handleDeleteRow = (index) => {
    onChange(messages.slice(0, index).concat(messages.slice(index + 1)))
  }

  const handleRowChange = (lineIndex, key) => (event) => {
    onChange(messages.map((line, i) => (lineIndex === i ? { ...line, [key]: event.target.value } : line)))
  }

  const textAreaValue = parseBroadcastMessages(messages)

  return (
    <Box {...props}>
      <textarea name='content' value={textAreaValue} disabled={disabled} required readOnly hidden />
      {messages.map(({ time_sec, message }, index) => (
        <Stack key={'line' + index} direction={'row'}>
          <StyledTextField
            required
            value={time_sec}
            name={'broadcast-time'}
            onChange={handleRowChange(index, 'time_sec')}
            placeholder='Time'
            sx={{ width: '100px' }}
            slotProps={{
              input: {
                type: 'number',
                min: 1,
                max: 999
              }
            }}
            disabled={disabled}
          />
          <StyledTextField
            required
            fullWidth
            value={message}
            name={'broadcast-message'}
            onChange={handleRowChange(index, 'message')}
            placeholder='Message'
            disabled={disabled}
          />
          {!disabled && (
            <IconButton color='error' onClick={() => handleDeleteRow(index)}>
              <DeleteIcon />
            </IconButton>
          )}
        </Stack>
      ))}
      {!disabled && (
        <Box sx={{ p: 1, borderWidth: 1, borderStyle: 'solid', borderColor: (theme) => theme.palette.divider }}>
          <Button onClick={handleAddRow} startIcon={<AddIcon />}>
            Add Message
          </Button>
        </Box>
      )}
    </Box>
  )
}
