import { useEffect, useRef, RefObject } from "react";

type EventListener = (event: Event) => void;

export default function useEventListener(
    eventType: string,
    callback: EventListener,
    element: Window | HTMLElement | null = window
): void {
    const callbackRef = useRef<EventListener>(callback);

    useEffect(() => {
        callbackRef.current = callback;
    }, [callback]);

    useEffect(() => {
        if (element == null) return;
        const handler = (e: Event) => callbackRef.current(e);
        element.addEventListener(eventType, handler);

        return () => element.removeEventListener(eventType, handler);
    }, [eventType, element]);
}
