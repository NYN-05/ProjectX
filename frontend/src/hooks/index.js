import { useState, useCallback, useRef } from 'react';

/**
 * Debounce hook - delays updating the value until after the specified delay
 * @param {string} value - The value to debounce
 * @param {number} delay - The debounce delay in milliseconds
 * @returns {string} - The debounced value
 */
export function useDebounce(value, delay = 300) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useCallback(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

/**
 * Local storage hook for persisting state
 * @param {string} key - The storage key
 * @param {any} initialValue - The initial value
 * @returns {[any, function]} - The stored value and setter function
 */
export function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(error);
      return initialValue;
    }
  });

  const setValue = useCallback((value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(error);
    }
  }, [key, storedValue]);

  return [storedValue, setValue];
}

/**
 * Async state hook for handling async operations with loading/error states
 * @returns {object} - Async state management helpers
 */
export function useAsync() {
  const [status, setStatus] = useState('idle');
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const execute = useCallback((promise) => {
    setStatus('pending');
    setData(null);
    setError(null);

    return promise
      .then((response) => {
        setStatus('success');
        setData(response);
        return response;
      })
      .catch((error) => {
        setStatus('error');
        setError(error);
        throw error;
      });
  }, []);

  const reset = useCallback(() => {
    setStatus('idle');
    setData(null);
    setError(null);
  }, []);

  return { execute, status, data, error, reset };
}

/**
 * Toast notification hook
 * @returns {object} - Toast helpers
 */
export function useToast() {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = 'info', duration = 3000) => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, duration);
  }, []);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  return { toasts, addToast, removeToast };
}

/**
 * Click outside hook for dropdowns and modals
 * @param {React.RefObject} ref - The reference to the element
 * @param {function} handler - The callback when clicked outside
 */
export function useClickOutside(ref, handler) {
  useCallback(() => {
    const listener = (event) => {
      if (!ref.current || ref.current.contains(event.target)) {
        return;
      }
      handler(event);
    };

    document.addEventListener('mousedown', listener);
    document.addEventListener('touchstart', listener);

    return () => {
      document.removeEventListener('mousedown', listener);
      document.removeEventListener('touchstart', listener);
    };
  }, [ref, handler]);
}

/**
 * Scroll position hook
 * @returns {number} - Current scroll position
 */
export function useScrollPosition() {
  const [scrollPosition, setScrollPosition] = useState(0);

  useCallback(() => {
    const updatePosition = () => {
      setScrollPosition(window.pageYOffset);
    };

    window.addEventListener('scroll', updatePosition);
    updatePosition();

    return () => window.removeEventListener('scroll', updatePosition);
  }, []);

  return scrollPosition;
}

/**
 * Fetch with retry hook
 * @param {function} fetchFn - The fetch function
 * @param {number} retries - Number of retries
 * @returns {object} - Fetch result with retry logic
 */
export function useFetchWithRetry(fetchFn, retries = 3, delay = 1000) {
  const [result, setResult] = useState({ loading: false, data: null, error: null });

  const execute = useCallback(async () => {
    setResult({ loading: true, data: null, error: null });

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const response = await fetchFn();
        setResult({ loading: false, data: response, error: null });
        return response;
      } catch (error) {
        if (attempt === retries) {
          setResult({ loading: false, data: null, error });
          throw error;
        }
        await new Promise(resolve => setTimeout(resolve, delay * (attempt + 1)));
      }
    }
  }, [fetchFn, retries, delay]);

  return { ...result, execute };
}
