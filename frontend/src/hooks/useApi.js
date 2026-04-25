import { useEffect, useState } from 'react';
import { apiUrl } from '../lib/api.js';

export function useApi(path) {
  const [data,    setData]    = useState(null);
  const [error,   setError]   = useState(null);
  const [version, setVersion] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setError(null);

    fetch(apiUrl(path))
      .then(r => r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`)))
      .then(d => { if (!cancelled) setData(d); })
      .catch(e => { if (!cancelled) setError(e); });

    return () => { cancelled = true; };
  }, [path, version]);

  function refetch() {
    setData(null);
    setVersion(v => v + 1);
  }

  return { data, error, loading: !data && !error, refetch };
}
