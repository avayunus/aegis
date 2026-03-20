import { useState, useEffect } from "react";
import { getMissions } from "../services/api";

/**
 * Hook to fetch and track mission list. Used when the mission
 * selector panel is built in Phase 2.
 */
export function useMission() {
  const [missions, setMissions] = useState<Array<Record<string, unknown>>>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMissions()
      .then((data) => setMissions(data.missions))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return { missions, loading };
}
