import {
  Divider,
  Drawer,
  FormControl,
  IconButton,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  styled,
  ToggleButton,
  ToggleButtonGroup,
  Toolbar,
  Typography
} from '@mui/material'
import { useEffect, useState } from 'react'
import CloseIcon from '@mui/icons-material/Close'

const ResponsiveDrawer = styled(Drawer)(({ theme }) => ({
  zIndex: theme.zIndex.modal,
  '& .MuiDrawer-paper': {
    width: '100%',
    [theme.breakpoints.up('sm')]: {
      width: '20rem'
    }
  }
}))

const Wrapper = styled(Stack)(({ theme }) => ({
  width: '100%',
  height: '100%',
  overflowX: 'hidden',
  paddingTop: theme.spacing(1),
  paddingBottom: theme.spacing(2),
  paddingLeft: theme.spacing(2),
  paddingRight: theme.spacing(2),
  gap: theme.spacing(2),
  [theme.breakpoints.up('sm')]: {
    width: '20rem'
  }
}))

const TableConfigDrawer = ({ table, name, open, onClose, config, children }) => {
  const [pendingConfig, setPendingConfig] = useState(null)

  const handleTableFontSizeChange = (e, fontSize) => {
    setPendingConfig((prev) => ({ ...prev, fontSize }))
  }

  const handleTableDensityChange = (e, density) => {
    setPendingConfig((prev) => ({ ...prev, density }))
  }

  const handleClose = () => {
    onClose(pendingConfig)
  }

  useEffect(() => {
    setPendingConfig({ ...config })
  }, [open])

  return (
    <ResponsiveDrawer open={open} onClose={handleClose}>
      <Toolbar
        disableGutters
        sx={{
          justifyContent: 'space-between',
          px: 2
        }}
      >
        <Typography sx={{ fontWeight: 500 }}>{name ? `${name} Table Settings` : 'Table Settings'}</Typography>
        <IconButton onClick={handleClose}>
          <CloseIcon />
        </IconButton>
      </Toolbar>
      <Divider />

      {pendingConfig && (
        <Wrapper>
          <div>
            <Typography
              sx={{
                mb: 1,
                fontSize: '0.85rem',
                textTransform: 'uppercase',
                letterSpacing: 1.5
              }}
            >
              Font Size
            </Typography>
            <ToggleButtonGroup
              value={pendingConfig.fontSize}
              exclusive
              onChange={handleTableFontSizeChange}
              aria-label='table font size change'
              fullWidth
            >
              <ToggleButton value='small' aria-label='small table'>
                Small
              </ToggleButton>
              <ToggleButton value='normal' aria-label='normal table'>
                Normal
              </ToggleButton>
              <ToggleButton value='large' aria-label='large table'>
                Large
              </ToggleButton>
            </ToggleButtonGroup>
          </div>
          <div>
            <Typography
              sx={{
                mb: 1,
                fontSize: '0.85rem',
                textTransform: 'uppercase',
                letterSpacing: 1.5
              }}
            >
              Table Density
            </Typography>
            <ToggleButtonGroup
              value={pendingConfig.density}
              exclusive
              onChange={handleTableDensityChange}
              aria-label='table density change'
              fullWidth
            >
              <ToggleButton value='dense' aria-label='dense table'>
                Dense
              </ToggleButton>
              <ToggleButton value='normal' aria-label='normal table'>
                Normal
              </ToggleButton>
              <ToggleButton value='comfortable' aria-label='comfortable table'>
                Comfortable
              </ToggleButton>
            </ToggleButtonGroup>
          </div>
          {table?.getState()?.pagination && (
            <div>
              <Typography
                sx={{
                  mb: 1,
                  fontSize: '0.85rem',
                  textTransform: 'uppercase',
                  letterSpacing: 1.5
                }}
              >
                Rows per page
              </Typography>
              <FormControl fullWidth sx={{ my: 1 }}>
                <InputLabel id='logs-table-page-size-select-label'>Size</InputLabel>
                <Select
                  labelId='logs-table-page-size-select-label'
                  id='logs-table-page-size-select'
                  value={table.getState().pagination.pageSize}
                  label='Age'
                  onChange={(e) => {
                    table.setPageSize(Number(e.target.value))
                  }}
                >
                  {[50, 100, 150, 250, 500].map((pageSize) => (
                    <MenuItem key={pageSize} value={pageSize}>
                      Show {pageSize}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </div>
          )}
          {children}
        </Wrapper>
      )}
    </ResponsiveDrawer>
  )
}

export default TableConfigDrawer
