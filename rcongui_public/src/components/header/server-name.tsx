'use client'

import { usePublicInfo } from '@/lib/queries/public-info'
import React from 'react'

export function ServerName() {
  const [publicInfo] = usePublicInfo()

  return <React.Fragment>{publicInfo?.name.name}</React.Fragment>
}
