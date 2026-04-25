import { useEffect, useMemo, useState } from 'react';
import { apiUrl } from '../lib/api.js';

const initialFilters = { search: '', status: '', category: '', model: '', risk: '' };
const initialSort    = { key: null, dir: 'asc' };

export function useCorpusFilter() {
  const [meta,     setMeta]     = useState(null);
  const [metaErr,  setMetaErr]  = useState(null);
  const [filters,  setFilters]  = useState(initialFilters);
  const [sort,     setSort]     = useState(initialSort);
  const [cols,     setCols]     = useState({});
  const [rows,     setRows]     = useState([]);
  const [count,    setCount]    = useState(0);
  const [loading,  setLoading]  = useState(true);

  useEffect(() => {
    let cancelled = false;
    fetch(apiUrl('/api/corpus/meta'))
      .then(r => r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`)))
      .then(m => {
        if (cancelled) return;
        setMeta(m);
        setCols(Object.fromEntries(m.columns.map(c => [c.key, c.defaultOn])));
      })
      .catch(e => { if (!cancelled) setMetaErr(e); });
    return () => { cancelled = true; };
  }, []);

  const queryString = useMemo(() => {
    const p = new URLSearchParams();
    if (filters.search)   p.set('search',   filters.search);
    if (filters.status)   p.set('status',   filters.status);
    if (filters.category) p.set('category', filters.category);
    if (filters.model)    p.set('model',    filters.model);
    if (filters.risk)     p.set('risk',     filters.risk);
    if (sort.key)         { p.set('sort', sort.key); p.set('dir', sort.dir); }
    return p.toString();
  }, [filters, sort]);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    const handle = setTimeout(() => {
      fetch(apiUrl(`/api/corpus${queryString ? '?' + queryString : ''}`))
        .then(r => r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`)))
        .then(d => {
          if (cancelled) return;
          setRows(d.rows);
          setCount(d.count);
          setLoading(false);
        })
        .catch(() => { if (!cancelled) setLoading(false); });
    }, filters.search ? 250 : 0);

    return () => { cancelled = true; clearTimeout(handle); };
  }, [queryString, filters.search]);

  function setFilter(key, value)  { setFilters(f => ({ ...f, [key]: value })); }
  function toggleColumn(key)      { setCols(c => ({ ...c, [key]: !c[key] })); }
  function reset() { setFilters(initialFilters); setSort(initialSort); }
  function toggleSort(key) {
    setSort(s => s.key === key
      ? { key, dir: s.dir === 'asc' ? 'desc' : 'asc' }
      : { key, dir: 'asc' });
  }

  return {
    meta, metaErr, rows, count, loading,
    filters, sort, cols,
    setFilter, toggleSort, toggleColumn, reset
  };
}
