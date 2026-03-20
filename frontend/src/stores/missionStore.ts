/**
 * Mission store — lightweight shared state for mission context.
 *
 * For MVP we use React context. If state management gets complex
 * in later phases, this can be migrated to Zustand or Jotai.
 */

import { createContext, useContext, useState, ReactNode } from "react";

interface MissionState {
  activeMissionId: string | null;
  setActiveMission: (id: string | null) => void;
  selectedAssetId: string | null;
  setSelectedAsset: (id: string | null) => void;
}

const MissionContext = createContext<MissionState | null>(null);

export function MissionProvider({ children }: { children: ReactNode }) {
  const [activeMissionId, setActiveMission] = useState<string | null>(
    "mission-001"
  );
  const [selectedAssetId, setSelectedAsset] = useState<string | null>(null);

  return (
    <MissionContext.Provider
      value={{
        activeMissionId,
        setActiveMission,
        selectedAssetId,
        setSelectedAsset,
      }}
    >
      {children}
    </MissionContext.Provider>
  );
}

export function useMissionStore() {
  const ctx = useContext(MissionContext);
  if (!ctx) throw new Error("useMissionStore must be inside MissionProvider");
  return ctx;
}
