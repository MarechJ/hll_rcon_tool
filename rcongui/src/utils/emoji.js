import React from "react";
import data from "@emoji-mart/data"
import { Emoji, getEmojiDataFromNative } from "emoji-mart";

export function getEmojiFlag(flag, size = 22) {
  const emo = getEmojiDataFromNative(flag, "apple", data);
  if (emo) {
    return <Emoji emoji={emo} set="apple" size={size} />;
  }
  return flag;
}
