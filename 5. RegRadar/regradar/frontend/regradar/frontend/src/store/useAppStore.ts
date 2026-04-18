import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AppStore {
  sessionId: string | null;
  selectedDomains: string[];
  setSessionId: (id: string) => void;
  setSelectedDomains: (domains: string[]) => void;
}

export const useAppStore = create<AppStore>()(
  persist(
    (set) => ({
      sessionId: null,
      selectedDomains: ['SEBI', 'RBI'],
      setSessionId: (id) => set({ sessionId: id }),
      setSelectedDomains: (domains) => set({ selectedDomains: domains }),
    }),
    { name: 'app-store' },
  ),
);
