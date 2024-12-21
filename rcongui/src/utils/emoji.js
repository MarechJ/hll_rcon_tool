import { init } from 'emoji-mart'
import data from "@emoji-mart/data/sets/15/twitter.json";

init({ data, set: "twitter" })

export function getEmoji(emoji, size = 22) {
  return <em-emoji id={emoji.id} set="twitter" size={size}></em-emoji>
}
