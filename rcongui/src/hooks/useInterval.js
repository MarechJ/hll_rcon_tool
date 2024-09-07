import React from "react";

export const useInterval = (callback, ms) => {
    const [error, setError] = React.useState(null);
    const [data, setData] = React.useState(null);
    const [loading, setLoading] = React.useState(true);
    const intervalRef = React.useRef(null);
    const savedCallbackRef = React.useRef(callback); // Store the latest callback

    // Update the callback ref when it changes
    React.useEffect(() => {
        savedCallbackRef.current = callback;
    }, [callback]);

    // The loading function that calls the current callback
    const load = React.useCallback(async () => {
        setLoading(true);
        try {
            const response = await savedCallbackRef.current(); // Always use the latest callback
            if (!response.ok) throw new Error("Failed to fetch data");
            const data = await response.json();
            setData(data);
            setError(null); // Clear previous errors
        } catch (err) {
            setError(err);
        } finally {
            setLoading(false);
        }
    }, []);

    const refresh = React.useCallback(async () => {
        clearInterval(intervalRef.current);
        await load();
        intervalRef.current = setInterval(load, ms);
    }, [load, ms]);

    React.useEffect(() => {
        // Initial load and set the interval
        load();
        intervalRef.current = setInterval(load, ms);

        // Cleanup interval on unmount or when dependencies change
        return () => {
            clearInterval(intervalRef.current);
        };
    }, [load, ms]);

    return { data, loading, error, refresh };
};

export const useAsyncInterval = (callback, ms) => {
    const [error, setError] = React.useState(null);
    const [data, setData] = React.useState(null);
    const [loading, setLoading] = React.useState(true);
    const intervalRef = React.useRef(null);
    const savedCallbackRef = React.useRef(callback); // Store the latest callback

    // Update the callback ref when it changes
    React.useEffect(() => {
        savedCallbackRef.current = callback;
    }, [callback]);

    const load = React.useCallback(async () => {
        const controller = new AbortController(); // Create a new AbortController
        const signal = controller.signal;

        setLoading(true);
        try {
            const response = await savedCallbackRef.current({ signal }); // Pass the signal to the fetch
            if (!response.ok) throw new Error("Failed to fetch data");
            const data = await response.json();
            setData(data);
            setError(null); // Clear any previous errors
        } catch (err) {
            if (err.name !== "AbortError") { // Handle only non-abort errors
                setError(err);
            }
        } finally {
            setLoading(false);
        }

        return controller; // Return the controller for cleanup purposes
    }, []);

    const refresh = React.useCallback(async () => {
        clearInterval(intervalRef.current);
        const controller = await load();
        intervalRef.current = setInterval(load, ms);

        return () => {
            controller?.abort(); // Ensure ongoing request is aborted
            clearInterval(intervalRef.current);
        };
    }, [load, ms]);

    React.useEffect(() => {
        let activeController;

        // Initial load and set the interval
        (async () => {
            activeController = await load();
            intervalRef.current = setInterval(load, ms);
        })();

        // Cleanup on unmount or dependency change
        return () => {
            activeController?.abort(); // Abort ongoing fetch if component unmounts
            clearInterval(intervalRef.current);
        };
    }, [load, ms]);

    return { data, loading, error, refresh };
};
