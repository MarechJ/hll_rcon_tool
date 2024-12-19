import { Checkbox, FormControlLabel, Popover } from '@mui/material'
import { Fragment, useState } from 'react'

export const WithPopver = ({ popoverContent, children }) => {
  const [anchorEl, setAnchorEl] = useState(null)

  const handlePopoverOpen = (event) => {
    setAnchorEl(event.currentTarget)
  }

  const handlePopoverClose = () => {
    setAnchorEl(null)
  }

  const open = Boolean(anchorEl)

  return (
    <Fragment>
      <div onMouseEnter={handlePopoverOpen} onMouseLeave={handlePopoverClose}>
        {children}
      </div>
      <Popover
        id='mouse-over-popover'
        open={open}
        anchorEl={anchorEl}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'left'
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'left'
        }}
        onClose={handlePopoverClose}
        disableRestoreFocus
      >
        {popoverContent}
      </Popover>
    </Fragment>
  )
}

export const ForwardCheckBox = ({ bool, onChange, label = 'Forward to all servers' }) => (
  <FormControlLabel
    control={
      <Checkbox
        checked={bool}
        onChange={(e) => {
          onChange(e.target.checked)
        }}
      />
    }
    label={label}
  />
)
