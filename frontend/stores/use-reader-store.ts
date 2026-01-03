import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface ReaderSettings {
  fontSize: number;
  fontFamily: 'sans' | 'serif' | 'mono';
  lineHeight: number;
  theme: 'light' | 'dark' | 'sepia';
  maxWidth: number;
}

interface ReaderStore {
  settings: ReaderSettings;
  updateSettings: (settings: Partial<ReaderSettings>) => void;
  resetSettings: () => void;
}

const defaultSettings: ReaderSettings = {
  fontSize: 18,
  fontFamily: 'serif',
  lineHeight: 1.6,
  theme: 'light',
  maxWidth: 800,
};

export const useReaderStore = create<ReaderStore>()(
  persist(
    (set) => ({
      settings: defaultSettings,
      updateSettings: (newSettings) =>
        set((state) => ({
          settings: { ...state.settings, ...newSettings },
        })),
      resetSettings: () => set({ settings: defaultSettings }),
    }),
    {
      name: 'forklore-reader-settings',
    }
  )
);
