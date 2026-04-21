import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// ── Auth Store ────────────────────────────────────────────────────────
interface AuthState {
  token: string | null;
  user: { id: string; email: string; name?: string } | null;
  _hasHydrated: boolean;
  setHasHydrated: (state: boolean) => void;
  setAuth: (token: string, user: { id: string; email: string; name?: string }) => void;
  clearAuth: () => void;
  isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      _hasHydrated: false,
      setHasHydrated: (val) => set({ _hasHydrated: val }),
      setAuth: (token, user) => {
        set({ token, user });
      },
      clearAuth: () => {
        set({ token: null, user: null });
      },
      isAuthenticated: () => !!get().token,
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token, user: state.user }),
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true);
      },
    }
  )
);

// ── Filter Store ──────────────────────────────────────────────────────
interface FilterState {
  searchQuery: string;
  selectedCategory: string | null;
  selectedLocation: string | null;
  selectedJobType: string | null;
  selectedSource: string | null;
  setSearchQuery: (query: string) => void;
  setCategory: (category: string | null) => void;
  setLocation: (location: string | null) => void;
  setJobType: (type: string | null) => void;
  setSource: (source: string | null) => void;
  reset: () => void;
}

export const useFilterStore = create<FilterState>((set) => ({
  searchQuery: '',
  selectedCategory: null,
  selectedLocation: null,
  selectedJobType: null,
  selectedSource: null,
  setSearchQuery: (query) => set({ searchQuery: query }),
  setCategory: (category) => set({ selectedCategory: category }),
  setLocation: (location) => set({ selectedLocation: location }),
  setJobType: (type) => set({ selectedJobType: type }),
  setSource: (source) => set({ selectedSource: source }),
  reset: () =>
    set({
      searchQuery: '',
      selectedCategory: null,
      selectedLocation: null,
      selectedJobType: null,
      selectedSource: null,
    }),
}));

// ── Theme Store ─────────────────────────────────────────────────────────
type Theme = 'light' | 'dark';

interface ThemeState {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      theme: 'light' as Theme,
      setTheme: (theme) => {
        set({ theme });
        // Apply dark class to document for Tailwind
        if (typeof window !== 'undefined') {
          document.documentElement.classList.toggle('dark', theme === 'dark');
        }
      },
      toggleTheme: () => {
        const newTheme = get().theme === 'light' ? 'dark' : 'light';
        set({ theme: newTheme });
        // Apply dark class to document for Tailwind
        if (typeof window !== 'undefined') {
          document.documentElement.classList.toggle('dark', newTheme === 'dark');
        }
      },
    }),
    {
      name: 'theme-storage',
      onRehydrateStorage: () => (state) => {
        // Apply dark class after hydration
        if (state?.theme === 'dark' && typeof window !== 'undefined') {
          document.documentElement.classList.add('dark');
        }
      },
    }
  )
);

// ── UI Store ──────────────────────────────────────────────────────────
interface UIState {
  sidebarOpen: boolean;
  selectedJobId: string | null;
  toggleSidebar: () => void;
  setSidebar: (open: boolean) => void;
  selectJob: (id: string | null) => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  selectedJobId: null,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setSidebar: (open) => set({ sidebarOpen: open }),
  selectJob: (id) => set({ selectedJobId: id }),
}));