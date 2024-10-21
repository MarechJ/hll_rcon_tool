import { isServer } from '@tanstack/react-query'

export function getBaseURL() {
    if (!isServer) {
      return ''
    }
    if (process.env.VERCEL_URL) {
      return `https://${process.env.VERCEL_URL}`
    }
    return 'http://localhost:3000'
  }