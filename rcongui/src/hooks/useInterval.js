import React from "react"

export const useInterval = (callback, ms) => {
    const [error, setError] = React.useState();
    const [data, setData] = React.useState();
    const [loading, setLoading] = React.useState(true);
    const intervalRef = React.useRef(null)

    const load = React.useCallback(async () => {
        setLoading(true);
        try {
            const response = await callback();
            if (!response.ok) throw new Error(response);
            const data = await response.json();
            setData(data);
        } catch (error) {
            setError(error);
        }
        setLoading(false);
    }, [callback])

    const refresh = async () => {
        clearInterval(intervalRef.current);
        await load();
        intervalRef.current = setInterval(load, ms);
    }
    
    React.useEffect(() => {
        load();
        intervalRef.current = setInterval(load, ms);
        return () => {
            clearInterval(intervalRef.current);
        }
    }, [load, ms])

    return { data, loading, error, refresh }
}