import Paper from '@mui/material/Paper'
import Divider from '@mui/material/Divider'
import IconButton from '@mui/material/IconButton'
import SearchIcon from '@mui/icons-material/Search'
import { Chip, InputBase } from '@mui/material'
import { styled } from '@mui/styles'

const SearchWrapper = styled('div')({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'start',
  width: '100%'
})

const StyledIconButton = styled(IconButton)({
  padding: 10
})

const StyledDivider = styled(Divider)({
  height: 28,
  margin: 4
})

const HiddableDivider = styled(Divider)(({ theme }) => ({
  width: '100%',
  [theme.breakpoints.up('sm')]: {
    display: 'none'
  }
}))

const ChipsWrapper = styled('div')(({ theme }) => ({
  display: 'flex',
  width: '100%',
  gap: 4,
  paddingTop: 8,
  paddingBottom: 8,
  justifyContent: 'start',
  alignItems: 'start',
  [theme.breakpoints.up('sm')]: {
    flexDirection: 'row',
    width: 'auto',
    paddingBottom: 0,
    paddingTop: 0
  }
}))

const StyledInputBase = styled(InputBase)(({ theme }) => ({
  root: {
    marginLeft: theme.spacing(1),
    flex: 1
  }
}))

export default function MapSearch({ onChange, onSearch, onFilter, filters }) {
  return (
    <Paper
      sx={(theme) => ({
        padding: '2px 4px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        [theme.breakpoints.up('sm')]: {
          flexDirection: 'row'
        }
      })}
    >
      <SearchWrapper>
        <StyledIconButton aria-label='search' onClick={onSearch} size='large'>
          <SearchIcon />
        </StyledIconButton>
        <StyledDivider orientation='vertical' />
        <InputBase
          sx={(theme) => ({
            marginLeft: theme.spacing(1),
            flex: 1
          })}
          placeholder='Search Map'
          inputProps={{ 'aria-label': 'search maps' }}
          onChange={onChange}
        />
        <StyledDivider orientation='vertical' />
      </SearchWrapper>
      <HiddableDivider orientation='horizontal' />
      <ChipsWrapper>
        {Object.entries(filters).map(([filter, isApplied]) => (
          <Chip
            key={filter}
            size='small'
            label={filter}
            color={isApplied ? 'primary' : 'default'}
            onClick={() => onFilter(filter)}
          />
        ))}
      </ChipsWrapper>
    </Paper>
  )
}
