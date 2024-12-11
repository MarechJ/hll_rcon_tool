import { Loader } from 'lucide-react'

export function Spinner() {
  return (
    <span>
      <Loader className="inline-block size-4 animate-spin" />
    </span>
  )
}
