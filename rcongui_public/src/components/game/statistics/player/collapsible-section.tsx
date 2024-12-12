import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { Button } from '@/components/ui/button'
import { ChevronsUpDownIcon } from 'lucide-react'
import React from 'react'

export function CollapsibleSection({
  name,
  defaultOpen,
  children,
}: {
  name: string
  defaultOpen?: boolean
  children: React.ReactNode
}) {
  const [isOpen, setIsOpen] = React.useState(defaultOpen ?? false)

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <CollapsibleTrigger asChild>
        <Button variant="ghost" size="default" className="w-full justify-start rounded-none pl-1">
          {name}
          <ChevronsUpDownIcon className="h-4 w-4" />
          <span className="sr-only">Toggle {name}</span>
        </Button>
      </CollapsibleTrigger>
      <CollapsibleContent>{children}</CollapsibleContent>
    </Collapsible>
  )
}
