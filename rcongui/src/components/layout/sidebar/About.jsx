import * as React from 'react'
import Button from '@mui/material/Button'
import Dialog from '@mui/material/Dialog'
import DialogActions from '@mui/material/DialogActions'
import DialogContent from '@mui/material/DialogContent'
import DialogContentText from '@mui/material/DialogContentText'
import DialogTitle from '@mui/material/DialogTitle'
import ListItem from '@mui/material/ListItem'
import ListItemText from '@mui/material/ListItemText'
import ListItemButton from '@mui/material/ListItemButton'
import { Divider, Stack, Typography, IconButton, Skeleton, useTheme, useMediaQuery } from '@mui/material'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faDiscord, faGithub } from '@fortawesome/free-brands-svg-icons'
import { faBook } from '@fortawesome/free-solid-svg-icons'
import siteConfig from '@/config/siteConfig'
import { cmd } from '@/utils/fetchUtils'
import { useQuery } from '@tanstack/react-query'
import dayjs from 'dayjs'
import { useGithubReleases } from '@/hooks/useGithubReleases'
import { Box } from '@mui/material'
import NewReleasesIcon from "@mui/icons-material/NewReleases";
import RefreshIcon from "@mui/icons-material/Refresh";
import { Suspense } from 'react';
import { ReleaseNotes } from './ReleaseNotes';

const isNewerVersion = (a, b) => {
  const [aMajor, aMinor, aPatch] = a.split('.');
  const [bMajor, bMinor, bPatch] = b.split('.');
  return aMajor >= bMajor && aMinor >= bMinor && aPatch >= bPatch;
}

export default function AboutDialog() {
  const [open, setOpen] = React.useState(false)
  const { releases, lastUpdate, unreadCount, markAsRead, forceUpdate } = useGithubReleases();
  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('md'));

  const { data: apiVersion, isLoading } = useQuery({
    queryKey: ['apiVersion'],
    queryFn: cmd.GET_VERSION,
    initialData: '0.0.0'
  })

  const handleClickOpen = () => {
    markAsRead();
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

  const latestReleaseVersion = releases?.[0]?.tag_name ?? ''
  const isUpToDate = isNewerVersion(apiVersion.trim(), latestReleaseVersion.trim())

  return (
    <React.Fragment>
      <ListItem disablePadding onClick={handleClickOpen}>
        <ListItemButton>
          <ListItemText 
            primary={
              <Box sx={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box>About</Box>
                {unreadCount > 0 && (
                  <NewReleasesIcon sx={{ fill: (theme) => theme.palette.secondary.main }} />
                )}
              </Box>
            }
            secondary={apiVersion}
          />
        </ListItemButton>
      </ListItem>
      <Dialog
        open={open}
        onClose={handleClose}
        aria-labelledby='about-dialog-title'
        aria-describedby='about-dialog-description'
        fullWidth
        fullScreen={isSmallScreen}
        maxWidth={'md'}
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

          <DialogContentText component={'section'} id='about-dialog-description' ref={descriptionElementRef} tabIndex={-1}>
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
                Last checked: {dayjs(lastUpdate).format('LLL')} <IconButton variant='text' size='small' aria-label='Refresh latest releases' onClick={() => {
                  forceUpdate();
                }}>
                  <RefreshIcon />
                </IconButton>
            </Typography>

            {releases.length > 0 && (
              <>
                <Suspense fallback={<Skeleton variant="rectangular" height={200} />}>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant='h6'>Latest Release {releases[0].name}</Typography>
                  <Typography variant='subtitle2' sx={{ mb: 2 }}>{dayjs(releases[0].published_at).format('LLL')}</Typography>
                  <ReleaseNotes release={releases[0]} />
                </Suspense>
              </>
            )}

          </DialogContentText>

        </DialogContent>

        <DialogActions>
          <Button onClick={handleClose}>Close</Button>
        </DialogActions>
      </Dialog>
    </React.Fragment>
  )
}
