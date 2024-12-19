import { ControlledTextInput } from '@/components/form/core/ControlledTextInput'
import { useTemplates } from '@/hooks/useTemplates'
import { MenuItem, Select } from '@mui/material'
import { useState } from 'react'

export const MessageField = ({ control, errors, setValue, ...props }) => {
  const templates = useTemplates('message')
  const [selectedTemplate, setSelectedTemplate] = useState('')
  const error = errors['message']
  const hasError = !!error

  const handleOnSelectChange = (event) => {
    const value = event.target.value ?? ''
    if (value === '') {
      setSelectedTemplate(value)
    } else {
      const template = templates[value]
      setSelectedTemplate(String(value))
      setValue('message', template.content, { shouldTouch: true })
    }
  }

  return (
    <>
      <ControlledTextInput
        error={hasError}
        name={'message'}
        label={'Message'}
        control={control}
        rules={{ required: 'Message is required' }}
        helperText={hasError ? error.message : 'The message displayed to the player.'}
        multiline
        minRows={5}
        fullWidth
      />
      <Select
        id='saved-messages-select'
        value={selectedTemplate}
        onChange={handleOnSelectChange}
        inputProps={{ 'aria-label': 'Saved Messages' }}
        fullWidth
        displayEmpty
      >
        <MenuItem value=''>
          <em>Saved Messages</em>
        </MenuItem>
        {templates.map((template, i) => {
          return (
            <MenuItem key={template.id} value={String(i)}>
              {template.title}
            </MenuItem>
          )
        })}
      </Select>
    </>
  )
}
