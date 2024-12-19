import { useMemo, useState, useEffect } from 'react'
import Box from '@mui/material/Box'
import ListItem from '@mui/material/ListItem'
import ListItemButton from '@mui/material/ListItemButton'
import ListItemText from '@mui/material/ListItemText'
import { cmd } from '@/utils/fetchUtils'
import { useLoaderData, useSubmit } from 'react-router-dom'
import { FixedSizeList } from 'react-window'
import {
  Button,
  Checkbox,
  Divider,
  FormControlLabel,
  IconButton,
  ListItemIcon,
  Paper,
  Stack,
  TextField
} from '@mui/material'
import DeleteIcon from '@mui/icons-material/Delete'
import SplitButton from '@/components/shared/SplitButton'
import { SearchInput } from '@/components/shared/SearchInput'
import debounce from 'lodash/debounce'
import { InputFileUpload } from '@/components/shared/InputFileUpload'
import exportFile from '@/utils/exportFile'

const INTENT = {
  SINGLE: 0,
  ALL: 1
}

export const loader = async () => {
  const profanities = await cmd.GET_PROFANITIES()
  return { profanities }
}

export const action = async ({ request }) => {
  const { profanities, ...rest } = Object.fromEntries(await request.formData())
  const payload = { profanities: profanities.length ? profanities.split(',') : [], ...rest }
  const result = await cmd.SET_PROFANITIES({ payload })
  return result
}

const ProfanityFilter = () => {
  const { profanities: serverProfanities } = useLoaderData()
  const [profanities, setProfanities] = useState(serverProfanities)
  const [checked, setChecked] = useState([])
  const [searched, setSearched] = useState('')
  const [newProfanity, setNewProfanity] = useState('')
  const submit = useSubmit()

  const filteredProfanities = useMemo(
    () => profanities.filter((word) => word.toLowerCase().includes(searched.toLowerCase())),
    [profanities, searched]
  )

  const handleToggle = (value) => () => {
    const currentIndex = checked.indexOf(value)
    const newChecked = [...checked]

    if (currentIndex === -1) {
      newChecked.push(value)
    } else {
      newChecked.splice(currentIndex, 1)
    }

    setChecked(newChecked)
  }

  const handleAddProfanity = () => {
    const word = newProfanity.trim()
    if (word) {
      setProfanities((prev) => [word, ...prev])
      setNewProfanity('')
    }
  }

  const handleDeleteSingleProfanity = (index) => {
    setProfanities((prev) => prev.slice(0, index).concat(prev.slice(index + 1)))
    setChecked((prev) => prev.filter((v) => v !== index))
  }

  const handleDeleteSelectedProfanities = () => {
    setProfanities((prev) => prev.filter((_, index) => !checked.includes(index)))
    setChecked([])
  }

  const handleToggleSelectAll = (e) => {
    if (e.target.checked) {
      setChecked(
        Array(filteredProfanities.length)
          .fill(null)
          .map((_, index) => index)
      )
    } else {
      setChecked([])
    }
  }

  const handleFileUpload = (event) => {
    const file = event.target.files[0]
    const reader = new FileReader()

    reader.onload = (e) => {
      const text = e.target.result
      const uploadedProfanities = text.split('\n')
      setProfanities(uploadedProfanities)
    }

    reader.readAsText(file)
  }

  const handleFileDownload = () => {
    exportFile(profanities, 'profanities')
  }

  const submitChanges = (intent) => () => {
    const formData = new FormData()
    formData.append('profanities', profanities)
    console.log(profanities)
    if (intent === INTENT.ALL) {
      formData.append('forward', true)
    }
    submit(formData, { method: 'POST' })
  }

  const onSearchedChange = debounce((event) => {
    setSearched(event.target.value)
  }, 500)

  useEffect(() => {
    setProfanities(serverProfanities)
  }, [serverProfanities])

  return (
    <Box
      sx={{
        maxWidth: (theme) => theme.breakpoints.values.md
      }}
    >
      <Stack
        component={Paper}
        direction={'row'}
        sx={{ p: 1, mb: 1 }}
        justifyContent={'end'}
        alignItems={'center'}
        gap={1}
      >
        <InputFileUpload text={'Upload'} color={'secondary'} onChange={handleFileUpload} accept={'.txt'} />
        <Button onClick={handleFileDownload} variant='contained' color='secondary'>
          Download
        </Button>
        <Box>
          <SplitButton
            options={[
              {
                name: 'Apply',
                buttonProps: {
                  onClick: submitChanges(INTENT.SINGLE)
                }
              },
              {
                name: 'Apply all servers',
                buttonProps: {
                  onClick: submitChanges(INTENT.ALL)
                }
              }
            ]}
          />
        </Box>
      </Stack>
      <Stack
        direction={'column'}
        gap={1}
        sx={{
          width: '100%',
          bgcolor: 'background.paper',
          padding: 1
        }}
      >
        <Stack direction={'row'} gap={1} sx={{ mb: 1, p: 0.5 }}>
          <TextField
            autoComplete={'off'}
            value={newProfanity}
            onChange={(e) => setNewProfanity(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleAddProfanity()}
            variant='standard'
            fullWidth
            label={'New profanity'}
          />
          <Button onClick={handleAddProfanity} variant='contained'>
            Add
          </Button>
        </Stack>
        <Stack direction={'row'} alignItems={'center'} justifyContent={'space-between'} gap={1} sx={{ mb: 1, p: 0.5 }}>
          <FormControlLabel
            sx={{ px: 0.25 }}
            label='Select'
            control={
              <Checkbox
                sx={{ mr: 1, '& .MuiSvgIcon-root': { fontSize: 16 } }}
                checked={checked.length === filteredProfanities.length && checked.length !== 0}
                indeterminate={checked.length > 0 && checked.length !== filteredProfanities.length}
                size='small'
                onChange={handleToggleSelectAll}
              />
            }
          />
          <Divider orientation='vertical' flexItem />
          <SearchInput onChange={onSearchedChange} placeholder='Search profanity' />
          <Divider orientation='vertical' flexItem />
          <Button
            onClick={handleDeleteSelectedProfanities}
            variant='contained'
            color='warning'
            disabled={!checked.length}
            sx={{ minWidth: 'fit-content' }}
          >
            Delete selected
          </Button>
        </Stack>
        <Divider orientation='horizontal' />
        <FixedSizeList
          height={600}
          itemSize={40}
          itemCount={filteredProfanities.length}
          itemData={filteredProfanities}
          overscanCount={5}
        >
          {({ index, style }) => {
            const labelId = `checkbox-list-label-${index}`
            return (
              <ListItem
                key={index}
                style={style}
                disablePadding
                secondaryAction={
                  <IconButton onClick={() => handleDeleteSingleProfanity(index)}>
                    <DeleteIcon />
                  </IconButton>
                }
              >
                <ListItemButton role={undefined} onClick={handleToggle(index)} dense>
                  <ListItemIcon>
                    <Checkbox
                      edge='start'
                      checked={checked.includes(index)}
                      tabIndex={-1}
                      disableRipple
                      inputProps={{ 'aria-labelledby': labelId }}
                    />
                  </ListItemIcon>
                  <ListItemText id={labelId} primary={filteredProfanities[index]} />
                </ListItemButton>
              </ListItem>
            )
          }}
        </FixedSizeList>
      </Stack>
    </Box>
  )
}

export default ProfanityFilter
