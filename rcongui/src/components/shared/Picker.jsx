import { styled } from '@mui/material/styles'
import Popper from '@mui/material/Popper'
import ClickAwayListener from '@mui/material/ClickAwayListener'
import Autocomplete, { autocompleteClasses } from '@mui/material/Autocomplete'
import ButtonBase from '@mui/material/ButtonBase'
import InputBase from '@mui/material/InputBase'
import Box from '@mui/material/Box'
import { Fragment, useState } from 'react'

const StyledAutocompletePopper = styled('div')(({ theme }) => ({
  [`& .${autocompleteClasses.paper}`]: {
    boxShadow: 'none',
    margin: 0,
    color: 'inherit',
    fontSize: 12
  },
  [`& .${autocompleteClasses.listbox}`]: {
    backgroundColor: '#fff',
    padding: 0,
    [`& .${autocompleteClasses.option}`]: {
      minHeight: 'auto',
      alignItems: 'center',
      gap: 4,
      textOverflow: 'ellipsis',
      whiteSpace: 'nowrap',
      padding: 8,
      borderBottom: `1px solid  ${' #eaecef'}`,
      '&[aria-selected="true"]': {
        backgroundColor: 'transparent'
      },
      [`&.${autocompleteClasses.focused}, &.${autocompleteClasses.focused}[aria-selected="true"]`]: {
        backgroundColor: theme.palette.action.hover
      },
      ...theme.applyStyles('dark', {
        borderBottom: `1px solid  ${'#30363d'}`
      })
    },
    ...theme.applyStyles('dark', {
      backgroundColor: '#1c2128'
    })
  },
  [`&.${autocompleteClasses.popperDisablePortal}`]: {
    position: 'relative'
  }
}))

function PopperComponent(props) {
  const { disablePortal, anchorEl, open, ...other } = props
  return <StyledAutocompletePopper {...other} />
}

const StyledPopper = styled(Popper)(({ theme }) => ({
  border: `1px solid ${'#e1e4e8'}`,
  boxShadow: `0 8px 24px ${'rgba(149, 157, 165, 0.2)'}`,
  backgroundColor: theme.palette.background.paper,
  borderRadius: 0,
  width: 300,
  zIndex: theme.zIndex.modal,
  fontSize: 12,
  ...theme.applyStyles('dark', {
    border: `1px solid ${'#30363d'}`,
    boxShadow: `0 8px 24px ${'rgb(1, 4, 9)'}`,
    color: '#c9d1d9'
  })
}))

const StyledInput = styled(InputBase)(({ theme }) => ({
  padding: 10,
  width: '100%',
  borderBottom: `1px solid ${theme.palette.divider}`,
  '& input': {
    borderRadius: 4,
    backgroundColor: '#fff',
    border: `1px solid ${theme.palette.divider}`,
    padding: 8,
    transition: theme.transitions.create(['border-color', 'box-shadow']),
    fontSize: 14,
    '&:focus': {
      boxShadow: `0px 0px 0px 3px ${'rgba(3, 102, 214, 0.3)'}`,
      borderColor: '#0366d6',
      ...theme.applyStyles('dark', {
        boxShadow: `0px 0px 0px 3px ${'rgb(12, 45, 107)'}`,
        borderColor: '#388bfd'
      })
    },
    ...theme.applyStyles('dark', {
      backgroundColor: theme.palette.background.paper,
      border: `1px solid ${theme.palette.divider}`
    })
  },
  ...theme.applyStyles('dark', {
    borderBottom: `1px solid ${theme.palette.divider}`
  })
}))

const Button = styled(ButtonBase)(({ theme }) => ({
  fontSize: 12,
  width: '100%',
  height: '100%',
  textAlign: 'left',
  fontWeight: 600,
  '&:hover,&:focus': {
    ...theme.applyStyles('dark', {})
  },
  '& span': {
    width: '100%'
  },
  '& svg': {
    width: 16,
    height: 16
  },
  ...theme.applyStyles('dark', {})
}))

export function Picker({ options, renderButton, id, description, onClose, ...props }) {
  const [anchorEl, setAnchorEl] = useState(null)
  const [value, setValue] = useState([])
  const [pendingValue, setPendingValue] = useState([])

  const handleClick = (event) => {
    setPendingValue(value)
    setAnchorEl(event.currentTarget)
  }

  const handleClose = () => {
    setValue(pendingValue)
    onClose(pendingValue)
    if (anchorEl) {
      anchorEl.focus()
    }
    setAnchorEl(null)
  }

  const open = Boolean(anchorEl)
  id = open ? id : undefined

  return (
    <Fragment>
      <Box sx={{ fontSize: 12 }}>{renderButton({ onClick: handleClick })}</Box>
      <StyledPopper id={id} open={open} anchorEl={anchorEl} placement='bottom-start'>
        <ClickAwayListener onClickAway={handleClose}>
          <div>
            <Box
              sx={(t) => ({
                borderBottom: `1px solid ${'#30363d'}`,
                padding: '8px 10px',
                fontWeight: 600,
                ...t.applyStyles('light', {
                  borderBottom: `1px solid ${'#eaecef'}`
                })
              })}
            >
              {description}
            </Box>
            <Autocomplete
              open
              multiple
              onClose={(event, reason) => {
                if (reason === 'escape') {
                  handleClose()
                }
              }}
              value={pendingValue}
              onChange={(event, newValue, reason) => {
                if (
                  event.type === 'keydown' &&
                  (event.key === 'Backspace' || event.key === 'Delete') &&
                  reason === 'removeOption'
                ) {
                  return
                }
                setPendingValue(newValue)
              }}
              disableCloseOnSelect
              renderTags={() => null}
              noOptionsText='No options'
              options={options}
              groupBy={(option) => option.team}
              renderInput={(params) => (
                <StyledInput
                  ref={params.InputProps.ref}
                  inputProps={params.inputProps}
                  autoFocus
                  placeholder='Filter options'
                />
              )}
              slots={{
                popper: PopperComponent
              }}
              {...props}
            />
          </div>
        </ClickAwayListener>
      </StyledPopper>
    </Fragment>
  )
}
