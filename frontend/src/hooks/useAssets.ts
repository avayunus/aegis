import { useState, useEffect } from "react";
import { getAssets } from "../services/api";

/**
 * Hook to fetch the initial asset list via REST.
 * After first load, real-time updates come through the WebSocket.
 */
export function useAssets() {
  const [assets, setAssets] = useState<Array<Record<string, unknown>>>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAssets()
      .then((data) => setAssets(data.assets))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return { assets, loading };
}
