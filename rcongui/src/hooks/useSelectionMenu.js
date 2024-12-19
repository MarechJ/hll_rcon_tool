import { useState, useMemo } from 'react'

export const useSelectionMenu = (options) => {
  const [search, setSearch] = useState('')
  const [isOpen, setIsOpen] = useState(false)

  const sortedOptions = useMemo(() => {
    if (!isOpen) return []
    return Object.keys(options).sort((a, b) => {
      if (options[a] && options[b]) {
        return a.localeCompare(b)
      }
      if (options[a]) return -1
      if (options[b]) return 1
      return a.localeCompare(b)
    })
  }, [isOpen])

  const hasSelected = useMemo(() => {
    return Object.values(options).some((value) => value)
  }, [options])

  const filteredOptions = sortedOptions.filter((optionName) => {
    return optionName.toLowerCase().includes(search.toLowerCase())
  })

  const onOpen = () => {
    setIsOpen(true)
  }

  const onClose = () => {
    setIsOpen(false)
    setSearch('')
  }

  return {
    search,
    setSearch,
    hasSelected,
    filteredOptions,
    onOpen,
    onClose
  }
}
