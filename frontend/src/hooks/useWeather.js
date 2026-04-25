import { useEffect, useState } from 'react';
import { apiUrl } from '../lib/api.js';

const REFRESH_MS = 10 * 60 * 1000;

export function useWeather() {
  const [data, setData]   = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const res  = await fetch(apiUrl('/api/weather'));
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = await res.json();
        if (!cancelled) { setData(json); setError(null); }
      } catch (err) {
        if (!cancelled) setError(err);
      }
    }

    load();
    const id = setInterval(load, REFRESH_MS);
    return () => { cancelled = true; clearInterval(id); };
  }, []);

  return { data, error, loading: !data && !error };
}
