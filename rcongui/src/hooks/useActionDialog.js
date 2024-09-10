import { ActionDialog } from '@/components/ActionDialog';
import React, { createContext, useState, useMemo } from 'react';

export const DialogContext = createContext();

export const ActionDialogProvider = ({ children }) => {
    const [open, setOpen] = useState(false);
    const [recipients, setRecipients] = useState(null);
    const [action, setAction] = useState(null);

    const contextValue = useMemo(() => ({
        open, setOpen, recipients, setRecipients, action, setAction
    }), [open, recipients, action]);

    return (
        <DialogContext.Provider value={contextValue}>
            {children}
            <ActionDialog />
        </DialogContext.Provider>
    );
};

export const useActionDialog = () => {
    const context = React.useContext(DialogContext);

    if (!context && process.env.NODE_ENV === 'development') {
        // In development, return a fallback or log a warning instead of throwing an error
        console.warn('useActionDialog must be used within an ActionDialogProvider');
        return {
          open: false,
          setOpen: () => {},
          action: null,
          setAction: () => {},
          recipients: null,
          setRecipients: () => {},
        };
      }
      
    // Check if context is undefined, indicating it was used outside of a provider
    if (!context) {
        throw new Error('useActionDialog must be used within an ActionDialogProvider');
    }
    return context;
};