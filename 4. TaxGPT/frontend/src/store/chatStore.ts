import { create } from 'zustand'

interface ChatMessage {
  question: string
  answer: string
}

interface ChatStore {
  history: ChatMessage[]
  addMessage: (question: string, answer: string) => void
  clearHistory: () => void
  getLastN: (n: number) => ChatMessage[]
}

export const useChatStore = create<ChatStore>((set, get) => ({
  history: [],

  addMessage: (question: string, answer: string) => {
    set((state) => ({
      history: [...state.history.slice(-4), { question, answer }],
    }))
  },

  clearHistory: () => set({ history: [] }),

  getLastN: (n: number) => {
    const { history } = get()
    return history.slice(-n)
  },
}))
