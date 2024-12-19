import { InputBase, Box, styled, IconButton } from '@mui/material'
import SearchIcon from '@mui/icons-material/Search'
import CloseIcon from '@mui/icons-material/Close'

const SearchWrapper = styled(Box)({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'start',
  width: '100%'
})

const StyledInput = styled(InputBase)({
  ml: 1,
  '& .MuiButtonBase-root': {
    display: 'none'
  },
  '&:hover .MuiButtonBase-root': {
    display: 'inline-flex'
  }
})

export function SearchInput({ ...props }) {
  const { sx, onClear, ...rest } = props
  return (
    <SearchWrapper sx={sx}>
      <Box sx={{ p: '10px', display: 'grid', alignItems: 'center' }}>
        <SearchIcon />
      </Box>
      <StyledInput
        placeholder={props.placeholder ?? 'Search'}
        inputProps={{
          'aria-label': props.placeholder?.toLowerCase() ?? 'search'
        }}
        endAdornment={
          onClear ? (
            <IconButton onClick={onClear} aria-label='clear' size='small'>
              <CloseIcon />
            </IconButton>
          ) : null
        }
        {...rest}
      />
    </SearchWrapper>
  )
}
