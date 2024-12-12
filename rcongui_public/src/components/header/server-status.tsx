'use client'

import React from 'react'
import { CircleAlertIcon, CirclePauseIcon, CirclePlayIcon } from 'lucide-react'
import { PublicInfo } from '@/types/api'
import { usePublicInfo } from '@/lib/queries/public-info'

function getStatus(publicInfo: PublicInfo) {
  // const ONE_MINUTE = 60
  if (publicInfo.player_count === 0 || publicInfo.time_remaining === 0) {
    return 'idle'
  }
  // TODO
  // Different case for skirmish or offensive!
  // else if (publicInfo.score.allied === 5 || publicInfo.score.axis === 5 || publicInfo.time_remaining < ONE_MINUTE ) {
  //     return "restart"
  // }
  return 'live'
}

export function ServerStatus() {
  const [publicInfo, { isLoading }] = usePublicInfo()
  let status

  if (isLoading || !publicInfo) {
    status = 'loading'
  } else {
    status = getStatus(publicInfo)
  }

  return (
    <span>
      {status === 'idle' ? (
        <CirclePauseIcon className="size-4 text-orange-500" />
      ) : status === 'live' ? (
        <CirclePlayIcon className="size-4 text-green-500" />
      ) : (
        <CircleAlertIcon className="size-4 text-red-500" />
      )}
    </span>
  )
}
