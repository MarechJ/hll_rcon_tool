import React from 'react'
import { getEmojiDataFromNative, Emoji, Picker } from 'emoji-mart'
import data from 'emoji-mart/data/all.json'

export function getEmojiFlag(flag, size=22) {
    const emo = getEmojiDataFromNative(flag, 'apple', data)
    if (emo) {
        return <Emoji emoji={emo} set='apple' size={size} />
    }
    return flag
}
