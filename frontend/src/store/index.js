import { create } from 'zustand'

export const useAuth = create((set) => ({
  token: localStorage.getItem('token') || '',
  user: null,
  setToken: (token) => {
    if (token) localStorage.setItem('token', token)
    else localStorage.removeItem('token')
    set({ token })
  },
  setUser: (user) => set({ user }),
  logout: () => {
    localStorage.removeItem('token')
    set({ token: '', user: null })
  },
}))

export const useRegion = create((set) => ({
  region: 'domestic', // domestic | international
  platform: 'xiaohongshu',
  setRegion: (region) => set({ region }),
  setPlatform: (platform) => set({ platform }),
}))
