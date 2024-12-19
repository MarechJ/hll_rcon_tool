import React from 'react'
import { Box, Typography } from '@mui/material'
import { Skeleton } from '@mui/material'
import moment from 'moment'

export function PlayerVipSummary({ player, vipExpiration }) {
  if (!player) {
    return (
      <>
        <Skeleton animation='wave' />
        <Skeleton animation='wave' />
        <Skeleton animation='wave' />
      </>
    )
  }

  return (
    <Box style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
      <Typography>
        Name: <span style={{ fontWeight: 500 }}>{getPlayerNames(player)}</span>
      </Typography>
      <Typography>
        Player ID: <span style={{ fontWeight: 500 }}>{player.get('player_id')}</span>
      </Typography>
      <Typography>
        VIP Expires: <span style={{ fontWeight: 500 }}>{getExpirationDate(vipExpiration)}</span>
      </Typography>
    </Box>
  )
}

function getExpirationDate(vipExpiration) {
  return vipExpiration ? `${moment(vipExpiration).format('lll')} (${moment(vipExpiration).fromNow()})` : '/'
}

function getPlayerNames(player) {
  let output = 'No name recorded yet'

  if (player?.get('names')) {
    output = player
      .get('names')
      .map((details) => details.get('name'))
      .join(', ')
  }

  if (player?.get('name')) {
    output = player.get('name')
  }

  return output
}
