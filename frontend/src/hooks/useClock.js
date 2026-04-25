import { useEffect, useState } from 'react';

function readClock() {
  const now = new Date();
  const hh = String(now.getHours()).padStart(2, '0');
  const mm = String(now.getMinutes()).padStart(2, '0');
  const dd = String(now.getDate()).padStart(2, '0');
  const mo = String(now.getMonth() + 1).padStart(2, '0');
  const yy = now.getFullYear();
  return { time: `${hh}:${mm}`, date: `${dd}/${mo}/${yy}` };
}

export function useClock() {
  const [clock, setClock] = useState(readClock);

  useEffect(() => {
    const id = setInterval(() => setClock(readClock()), 30_000);
    return () => clearInterval(id);
  }, []);

  return clock;
}
