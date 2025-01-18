'use client'

import * as React from 'react'
import * as TooltipPrimitive from '@radix-ui/react-tooltip'

import { cn } from '@/lib/utils'

import { createContext } from 'react';
import {useIsMobile} from "@/hooks/use-mobile";

type TooltipTriggerContextType = {
  open: boolean;
  setOpen: React.Dispatch<React.SetStateAction<boolean>>;
};

const TooltipTriggerContext = createContext<TooltipTriggerContextType>({
  open: false,
  setOpen: () => {},
});

const TooltipProvider = TooltipPrimitive.Provider

const Tooltip: React.FC<TooltipPrimitive.TooltipProps> = ({ children, ...props }) => {
  const [open, setOpen] = React.useState<boolean>(props.defaultOpen ?? false);

  const isMobile = useIsMobile();

  return (
    <TooltipPrimitive.Root
      delayDuration={isMobile ? 200 : props.delayDuration}
      onOpenChange={(e) => {
        setOpen(e);
      }}
      open={open}
    >
      <TooltipTriggerContext.Provider value={{ open, setOpen }}>
        {children}
      </TooltipTriggerContext.Provider>
    </TooltipPrimitive.Root>
  );
};

const TooltipTrigger = React.forwardRef<
  React.ElementRef<typeof TooltipPrimitive.Trigger>,
  React.ComponentPropsWithoutRef<typeof TooltipPrimitive.Trigger>
>(({ children, ...props }, ref) => {
  const isMobile = useIsMobile();
  const { setOpen } = React.useContext(TooltipTriggerContext);

  return (
    <TooltipPrimitive.Trigger
      ref={ref}
      {...props}
      onContextMenu={(e) => {
        e.preventDefault();
        setOpen(true);
      }}
    >
      {children}
    </TooltipPrimitive.Trigger>
  );
});

const TooltipContent = React.forwardRef<
  React.ElementRef<typeof TooltipPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof TooltipPrimitive.Content>
>(({ className, sideOffset = 4, ...props }, ref) => (
  <TooltipPrimitive.Content
    ref={ref}
    sideOffset={sideOffset}
    className={cn(
      'z-50 overflow-hidden rounded-md border bg-popover px-3 py-1.5 text-sm text-popover-foreground shadow-md animate-in fade-in-0 zoom-in-95 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2',
      className,
    )}
    {...props}
  />
))
TooltipContent.displayName = TooltipPrimitive.Content.displayName

export { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider }
