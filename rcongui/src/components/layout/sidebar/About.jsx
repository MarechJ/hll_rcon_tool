import * as React from 'react'
import Button from '@mui/material/Button'
import Dialog from '@mui/material/Dialog'
import DialogActions from '@mui/material/DialogActions'
import DialogContent from '@mui/material/DialogContent'
import DialogContentText from '@mui/material/DialogContentText'
import DialogTitle from '@mui/material/DialogTitle'
import InfoIcon from '@mui/icons-material/Info'
import ListItem from '@mui/material/ListItem'
import ListItemIcon from '@mui/material/ListItemIcon'
import ListItemText from '@mui/material/ListItemText'
import ListItemButton from '@mui/material/ListItemButton'
import { Divider, Stack, Typography } from '@mui/material'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faDiscord, faGithub } from '@fortawesome/free-brands-svg-icons'
import { faBook } from '@fortawesome/free-solid-svg-icons'
import siteConfig from '@/config/siteConfig'
import { cmd } from '@/utils/fetchUtils'
import { useQuery } from '@tanstack/react-query'
import localforage from 'localforage'
import dayjs from 'dayjs'

export default function AboutDialog() {
  const [open, setOpen] = React.useState(false)
  const [releasesStore, setReleasesStore] = React.useState({
    lastUpdate: null,
    releases: []
  })

  const { data: apiVersion, isLoading } = useQuery({
    queryKey: ['apiVersion'],
    queryFn: cmd.GET_VERSION,
    initialData: '0.0.0'
  })

  React.useEffect(() => {
    const loadReleases = async () => {
      const storedStore = await localforage.getItem('releases')
      setReleasesStore(storedStore)
    }
    loadReleases()
  }, [])

  const handleClickOpen = () => {
    setOpen(true)
  }

  const handleClose = () => {
    setOpen(false)
  }

  const descriptionElementRef = React.useRef(null)
  React.useEffect(() => {
    if (open) {
      const { current: descriptionElement } = descriptionElementRef
      if (descriptionElement !== null) {
        descriptionElement.focus()
      }
    }
  }, [open])

  const latestReleaseVersion = releasesStore.releases?.[0]?.name ?? ''
  const isUpToDate = latestReleaseVersion.trim() === apiVersion.trim()

  return (
    <React.Fragment>
      <ListItem disablePadding onClick={handleClickOpen}>
        <ListItemButton>
          <ListItemIcon sx={{ minWidth: 0 }}>
            <InfoIcon />
          </ListItemIcon>
          <ListItemText primary='About' />
        </ListItemButton>
      </ListItem>
      <Dialog
        open={open}
        onClose={handleClose}
        aria-labelledby='about-dialog-title'
        aria-describedby='about-dialog-description'
        fullWidth
        maxWidth='md'
      >
        <DialogTitle id='about-dialog-title'>About</DialogTitle>
        <DialogContent dividers={true}>
          <Stack direction={['column', 'row']} gap={2} sx={{ mb: 2 }}>
            <Button
              size='small'
              variant='contained'
              LinkComponent='a'
              href={siteConfig.documentationUrl}
              target='_blank'
              startIcon={<FontAwesomeIcon icon={faBook} />}
            >
              Documentation
            </Button>
            <Button
              size='small'
              variant='contained'
              LinkComponent='a'
              href={siteConfig.discordUrl}
              target='_blank'
              startIcon={<FontAwesomeIcon icon={faDiscord} />}
            >
              Need Help?
            </Button>
            <Button
              size='small'
              variant='contained'
              LinkComponent='a'
              href={siteConfig.githubUrl}
              target='_blank'
              startIcon={<FontAwesomeIcon icon={faGithub} />}
            >
              Found an issue? Submit a PR!
            </Button>
          </Stack>
          <DialogContentText id='about-dialog-description' ref={descriptionElementRef} tabIndex={-1}>
            <Typography variant='h5'>Hell Let Loose (HLL) Community RCON (CRCON)</Typography>
            <Typography>
              An extended RCON tool for Hell Let Loose, meant to replace the official tool and go WAY beyond.
            </Typography>
            <Divider sx={{ my: 2 }} />
            <Typography variant='body1'>API Version: {isLoading ? 'Loading...' : apiVersion}</Typography>
            <Typography variant='subtitle2'>
                {isUpToDate ? 'You are up to date! 🥳' : 'Your app is out of date 💩. You can update now.'}
            </Typography>
            <Typography variant='subtitle2'>
                Last checked: {dayjs(releasesStore.lastUpdate).format('LLL')}
            </Typography>
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Close</Button>
        </DialogActions>
      </Dialog>
    </React.Fragment>
  )
}
