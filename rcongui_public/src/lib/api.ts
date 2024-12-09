import { CRCON_Response } from '@/types/api'
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_CRCON_API_URL || process.env.REACT_APP_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

export const fetchApi = async <T>(path: string): Promise<CRCON_Response<T>> => {
  const response = await api.get<CRCON_Response<T>>(path)

  if (response.status >= 400) {
    throw new Error(`Failed to fetch data from ${path}`)
  }

  return response.data
}
