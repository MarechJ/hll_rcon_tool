import React from 'react';
import data from '@emoji-mart/data'
import { init } from 'emoji-mart'

init({ data })

export function getEmojiFlag(flag) {
  return flag
}