import axios from 'axios'
import { useApiKeyStore } from '../store/apiKeyStore'

const API_BASE_URL = '/api/v1'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
})

// Interceptor to add API key headers
apiClient.interceptors.request.use((config) => {
  const store = useApiKeyStore.getState()

  if (store.provider) {
    config.headers['X-Provider'] = store.provider
  }

  // Add provider-specific API key
  if (store.provider === 'gemini' && store.geminiKey) {
    config.headers['X-Gemini-Key'] = store.geminiKey
  } else if (store.provider === 'anthropic' && store.anthropicKey) {
    config.headers['X-Anthropic-Key'] = store.anthropicKey
  } else if (store.provider === 'openai' && store.openaiKey) {
    config.headers['X-OpenAI-Key'] = store.openaiKey
  } else if (store.provider === 'openrouter' && store.openrouterKey) {
    config.headers['X-OpenRouter-Key'] = store.openrouterKey
    if (store.openrouterModel) {
      config.headers['X-OpenRouter-Model'] = store.openrouterModel
    }
  } else if (store.provider === 'ollama') {
    if (store.ollamaUrl) {
      config.headers['X-Ollama-URL'] = store.ollamaUrl
    }
    if (store.ollamaModel) {
      config.headers['X-Ollama-Model'] = store.ollamaModel
    }
  }

  return config
})

// Error handler
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 400) {
      console.error('API validation error:', error.response.data)
    }
    return Promise.reject(error)
  }
)

export default apiClient
