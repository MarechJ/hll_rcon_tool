import { ActionDialog } from '@/components/ActionDialog';
import React, { createContext, useState } from 'react';

export const DialogContext = createContext();

export const ActionDialogProvider = ({ children }) => {
    const [open, setOpen] = useState(false);
    const [recipients, setRecipients] = useState(null);
    const [action, setAction] = useState(null);

    return (
        <DialogContext.Provider
            value={{ open, setOpen, recipients, setRecipients, action, setAction }}
        >
            {children}
            <ActionDialog />
        </DialogContext.Provider>
    );
};

export const useActionDialog = () => {
    return React.useContext(DialogContext);
};