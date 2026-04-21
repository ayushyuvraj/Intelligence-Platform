import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

export type Provider = 'gemini' | 'anthropic' | 'openai' | 'openrouter' | 'ollama'

interface ApiKeyStore {
  provider: Provider
  geminiKey: string
  anthropicKey: string
  openaiKey: string
  openrouterKey: string
  openrouterModel: string
  ollamaUrl: string
  ollamaModel: string

  // Actions
  setProvider: (provider: Provider) => void
  setGeminiKey: (key: string) => void
  setAnthropicKey: (key: string) => void
  setOpenAIKey: (key: string) => void
  setOpenRouterKey: (key: string) => void
  setOpenRouterModel: (model: string) => void
  setOllamaUrl: (url: string) => void
  setOllamaModel: (model: string) => void
}

export const useApiKeyStore = create<ApiKeyStore>()(
  persist(
    (set) => ({
      provider: 'gemini',
      geminiKey: '',
      anthropicKey: '',
      openaiKey: '',
      openrouterKey: '',
      openrouterModel: 'openai/gpt-4',
      ollamaUrl: 'http://localhost:11434',
      ollamaModel: 'mistral',

      setProvider: (provider) => set({ provider }),
      setGeminiKey: (geminiKey) => set({ geminiKey }),
      setAnthropicKey: (anthropicKey) => set({ anthropicKey }),
      setOpenAIKey: (openaiKey) => set({ openaiKey }),
      setOpenRouterKey: (openrouterKey) => set({ openrouterKey }),
      setOpenRouterModel: (openrouterModel) => set({ openrouterModel }),
      setOllamaUrl: (ollamaUrl) => set({ ollamaUrl }),
      setOllamaModel: (ollamaModel) => set({ ollamaModel }),
    }),
    {
      name: 'api-key-store',
      storage: createJSONStorage(() => localStorage),
    }
  )
)
