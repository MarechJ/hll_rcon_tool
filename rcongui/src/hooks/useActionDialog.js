import { ActionDialog } from '@/features/player-action/ActionDialog';
import { get, handleHttpError } from '@/utils/fetchUtils';
import { useQueries, useQueryClient } from "@tanstack/react-query";
import React, { createContext, useEffect, useMemo, useReducer } from 'react';

export const DialogContext = createContext();

// Initial state
const initialState = {
    open: false,
    recipients: null,
    action: null,
    contextData: {},  // Store additional context data (like blacklists)
};

// Action types
const SET_STATE = 'SET_STATE';
const SET_CONTEXT_DATA = 'SET_CONTEXT_DATA';
const RESET = 'RESET';

// Reducer function
const reducer = (state, action) => {
    switch (action.type) {
        case SET_STATE:
            return {
                ...state,
                open: !action.payload.context, // initially set open to false if context provided
                recipients: action.payload.recipients,
                action: action.payload.action,
                contextData: {},  // Reset context data
            };

        case SET_CONTEXT_DATA:
            return {
                ...state,
                contextData: action.payload,
                open: true,  // open only when context data is fetched
            };

        case RESET:
            return initialState;

        default:
            return state;
    }
};

export const ActionDialogProvider = ({ children }) => {
    const [state, dispatch] = useReducer(reducer, initialState);
    const queryClient = useQueryClient();  // Access react-query's client for manual queries

    // The openDialog function now handles fetching and dispatching
    const openDialog = async (actionValue, recipientsValue) => {
        // Step 1: Set the initial state with the action and recipients
        dispatch({
            type: SET_STATE,
            payload: {
                recipients: recipientsValue,
                action: actionValue,
            },
        });

        if (!actionValue?.context?.length) return;

        try {
            // Step 2: Fetch all the context-based data using Promise.all and queryClient
            const promises = actionValue.context.map((apiKey) =>
                queryClient.fetchQuery({
                    queryKey: [apiKey],
                    queryFn: async () => {
                        const response = await get(apiKey);
                        handleHttpError(response)
                        const data = await response.json()
                        if (data && !data.failed) {
                            return data.result
                        }
                    },
                    staleTime: 60 * 1000,
                })
            );

            // Wait for all queries to complete
            const results = await Promise.all(promises);

            // Step 3: Construct the contextData object with the fetched results
            const contextData = actionValue.context.reduce((acc, apiKey, index) => {
                acc[apiKey] = results[index];
                return acc;
            }, {});

            // Step 4: Dispatch the context data after all queries are completed
            dispatch({
                type: SET_CONTEXT_DATA,
                payload: contextData,
            });
        } catch (error) {
            console.error('Failed to fetch context data', error);
            // Handle the error, possibly dispatch an error state
        }
    };

    const closeDialog = () => {
        dispatch({
            type: RESET,
        })
    }

    const contextValue = useMemo(() => ({ 
        state,
        openDialog,
        closeDialog 
    }), [state, openDialog, closeDialog])

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
            state: initialState,
            openDialog: () => { },
            closeDialog: () => { },
        };
    }

    // Check if context is undefined, indicating it was used outside of a provider
    if (!context) {
        throw new Error('useActionDialog must be used within an ActionDialogProvider');
    }
    return context;
};