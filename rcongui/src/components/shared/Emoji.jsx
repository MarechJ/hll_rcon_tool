import { getEmojiDataFromNative, init } from 'emoji-mart'
import data from "@emoji-mart/data/sets/14/twitter.json";
import React from 'react';

init({ data, set: "twitter" })

export default function Emoji({ emoji: anEmoji, size = 18 }) {
  const [emojiData, setEmojiData] = React.useState(null);
  
  React.useEffect(() => {
    async function loadEmoji() {
      try {
        // If emoji from emoji-mart is provided, use it directly
        if (anEmoji.id) {
          setEmojiData(anEmoji);
          return;
        }
        
        // If just an emoji string is provided, find it in the data
        const data = await getEmojiDataFromNative(anEmoji);
        if (data) {
          setEmojiData(data);
        }
      } catch (error) {
        console.error('Error loading emoji:', error);
      }
    }
    
    loadEmoji();
  }, [anEmoji]);

  if (!emojiData) return null;
  
  return <em-emoji id={emojiData.id} set="twitter" size={size}></em-emoji>;
}
