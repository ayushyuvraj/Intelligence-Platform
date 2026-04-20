import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Eye, EyeOff, ExternalLink, Key, Check, AlertCircle } from 'lucide-react'
import { useApiKeyStore, type Provider } from '../store/apiKeyStore'

interface ProviderConfig {
  id: Provider
  name: string
  icon: React.ReactNode
  color: string
  border: string
  keyLabel: string
  keyPlaceholder: string
  docsUrl: string
  free?: boolean
}

const PROVIDERS_CONFIG: ProviderConfig[] = [
  {
    id: 'gemini',
    name: 'Google Gemini',
    color: 'text-blue-400',
    border: 'border-blue-500/30',
    keyLabel: 'API Key',
    keyPlaceholder: 'AIzaSy...',
    docsUrl: 'https://aistudio.google.com/app/apikey',
    icon: (
      <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none">
        <path d="M12 2L9.5 9.5H2L8 13.5L5.5 21L12 17L18.5 21L16 13.5L22 9.5H14.5L12 2Z" fill="url(#g1)" />
        <defs><linearGradient id="g1" x1="2" y1="2" x2="22" y2="21"><stop offset="0%" stopColor="#4285F4" /><stop offset="100%" stopColor="#34A853" /></linearGradient></defs>
      </svg>
    ),
  },
  {
    id: 'openai',
    name: 'OpenAI',
    color: 'text-emerald-400',
    border: 'border-emerald-500/30',
    keyLabel: 'API Key',
    keyPlaceholder: 'sk-...',
    docsUrl: 'https://platform.openai.com/api-keys',
    icon: <div className="h-5 w-5 rounded bg-gradient-to-br from-emerald-500 to-emerald-700 flex items-center justify-center text-white text-xs font-bold">O</div>,
  },
  {
    id: 'anthropic',
    name: 'Anthropic Claude',
    color: 'text-orange-400',
    border: 'border-orange-500/30',
    keyLabel: 'API Key',
    keyPlaceholder: 'sk-ant-...',
    docsUrl: 'https://console.anthropic.com/settings/keys',
    icon: <div className="h-5 w-5 rounded bg-gradient-to-br from-orange-500 to-orange-700 flex items-center justify-center text-white text-xs font-bold">C</div>,
  },
  {
    id: 'openrouter',
    name: 'OpenRouter',
    color: 'text-violet-400',
    border: 'border-violet-500/30',
    keyLabel: 'API Key',
    keyPlaceholder: 'sk-or-...',
    docsUrl: 'https://openrouter.ai/keys',
    free: true,
    icon: <div className="h-5 w-5 rounded bg-gradient-to-br from-violet-500 to-purple-700 flex items-center justify-center text-white text-xs font-black">OR</div>,
  },
]

interface APIKeyManagerProps {
  open: boolean
  onClose: () => void
}

export function APIKeyManager({ open, onClose }: APIKeyManagerProps) {
  const store = useApiKeyStore()
  const [keys, setKeys] = useState({
    gemini: store.geminiKey,
    openai: store.openaiKey,
    anthropic: store.anthropicKey,
    openrouter: store.openrouterKey,
  })
  const [showKeys, setShowKeys] = useState<Record<Provider, boolean>>({
    gemini: false,
    openai: false,
    anthropic: false,
    openrouter: false,
    ollama: false,
  })
  const [activeProvider, setActiveProvider] = useState<Provider>(store.provider)
  const [saved, setSaved] = useState(false)

  const configuredProviders = PROVIDERS_CONFIG.filter((p) => keys[p.id as keyof typeof keys])
  const hasAtLeastOne = configuredProviders.length > 0

  const handleSave = () => {
    if (!hasAtLeastOne) return

    // Save all keys
    if (keys.gemini) store.setGeminiKey(keys.gemini)
    if (keys.openai) store.setOpenAIKey(keys.openai)
    if (keys.anthropic) store.setAnthropicKey(keys.anthropic)
    if (keys.openrouter) store.setOpenRouterKey(keys.openrouter)

    // Set active provider
    store.setProvider(activeProvider)

    setSaved(true)
    setTimeout(() => {
      setSaved(false)
      onClose()
    }, 1200)
  }

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm"
          />

          <motion.div
            initial={{ opacity: 0, scale: 0.94, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.94, y: 20 }}
            transition={{ type: 'spring', stiffness: 400, damping: 35 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none"
          >
            <div
              className="pointer-events-auto w-full max-w-3xl rounded-2xl border border-white/10 overflow-hidden max-h-[90vh] overflow-y-auto"
              style={{ background: 'rgba(8,12,22,0.98)', backdropFilter: 'blur(32px)' }}
            >
              {/* Header */}
              <div className="sticky top-0 z-10 flex items-center justify-between border-b border-white/8 p-6" style={{ background: 'rgba(8,12,22,0.95)' }}>
                <div>
                  <h2 className="font-bold text-white text-lg">Configure AI Providers</h2>
                  <p className="text-xs text-gray-500 mt-1">Add API keys for the providers you want to use</p>
                </div>
                <motion.button
                  whileHover={{ scale: 1.1, rotate: 90 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={onClose}
                  className="rounded-lg p-1.5 text-gray-500 hover:bg-white/8 hover:text-white transition-colors shrink-0"
                >
                  <X className="h-5 w-5" />
                </motion.button>
              </div>

              <div className="p-6 space-y-6">
                {/* Provider inputs */}
                <div className="space-y-4">
                  <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Add API Keys</h3>
                  <div className="space-y-3">
                    {PROVIDERS_CONFIG.map((provider) => (
                      <motion.div
                        key={provider.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="rounded-xl border border-white/8 p-4 bg-white/[0.02]"
                      >
                        <div className="flex items-center gap-3 mb-3">
                          {provider.icon}
                          <div className="flex-1">
                            <p className="font-semibold text-sm text-white">{provider.name}</p>
                            {provider.free && (
                              <p className="text-[11px] text-emerald-400">Free tier available</p>
                            )}
                          </div>
                          {keys[provider.id as keyof typeof keys] && (
                            <div className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-500/20">
                              <Check className="h-4 w-4 text-emerald-400" />
                            </div>
                          )}
                        </div>

                        <div className="relative">
                          <input
                            type={showKeys[provider.id] ? 'text' : 'password'}
                            value={keys[provider.id as keyof typeof keys]}
                            onChange={(e) =>
                              setKeys({
                                ...keys,
                                [provider.id]: e.target.value,
                              })
                            }
                            placeholder={provider.keyPlaceholder}
                            className="w-full rounded-lg border border-white/10 bg-black/40 px-4 py-2 pr-20 text-sm text-white placeholder:text-gray-600 focus:border-indigo-500/50 focus:outline-none focus:ring-1 focus:ring-indigo-500/20 font-mono"
                          />
                          <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
                            <button
                              type="button"
                              onClick={() =>
                                setShowKeys({
                                  ...showKeys,
                                  [provider.id]: !showKeys[provider.id],
                                })
                              }
                              className="p-1 text-gray-500 hover:text-gray-300 transition-colors"
                            >
                              {showKeys[provider.id] ? (
                                <EyeOff className="h-4 w-4" />
                              ) : (
                                <Eye className="h-4 w-4" />
                              )}
                            </button>
                            <a
                              href={provider.docsUrl}
                              target="_blank"
                              rel="noreferrer"
                              className="p-1 text-gray-500 hover:text-indigo-400 transition-colors"
                              title="Get API key"
                              onClick={(e) => e.stopPropagation()}
                            >
                              <ExternalLink className="h-4 w-4" />
                            </a>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>

                {/* Select active provider */}
                {hasAtLeastOne && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="rounded-xl border border-indigo-500/20 bg-indigo-500/10 p-4"
                  >
                    <label className="text-sm font-semibold text-gray-300 block mb-3">
                      {configuredProviders.length === 1
                        ? 'Default Provider (Only option configured)'
                        : 'Select Default Provider'}
                    </label>
                    <select
                      value={activeProvider}
                      onChange={(e) => setActiveProvider(e.target.value as Provider)}
                      className="w-full rounded-lg border border-indigo-500/30 bg-indigo-500/5 px-4 py-2.5 text-sm text-white focus:border-indigo-500/50 focus:outline-none focus:ring-1 focus:ring-indigo-500/20"
                    >
                      {configuredProviders.map((p) => (
                        <option key={p.id} value={p.id} className="bg-gray-900">
                          {p.name}
                        </option>
                      ))}
                    </select>
                    <p className="text-xs text-gray-400 mt-2">
                      You can change this anytime. Other providers will still be available.
                    </p>
                  </motion.div>
                )}

                {/* Warning if no keys */}
                {!hasAtLeastOne && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="rounded-xl border border-amber-500/20 bg-amber-500/10 p-4 flex gap-3"
                  >
                    <AlertCircle className="h-5 w-5 text-amber-400 shrink-0 mt-0.5" />
                    <div className="text-sm">
                      <p className="font-semibold text-amber-100">Add at least one API key</p>
                      <p className="text-amber-200/70 text-xs mt-1">You need to configure at least one provider to use the AI features</p>
                    </div>
                  </motion.div>
                )}

                {/* Footer */}
                <div className="flex items-center gap-3 pt-2">
                  <motion.button
                    whileHover={hasAtLeastOne ? { scale: 1.02 } : {}}
                    whileTap={hasAtLeastOne ? { scale: 0.97 } : {}}
                    onClick={handleSave}
                    disabled={!hasAtLeastOne}
                    className="flex flex-1 items-center justify-center gap-2 rounded-xl py-3 text-sm font-semibold text-white disabled:opacity-40 disabled:cursor-not-allowed transition-all"
                    style={{
                      background: saved
                        ? 'linear-gradient(135deg, #10b981, #059669)'
                        : hasAtLeastOne
                          ? 'linear-gradient(135deg, #6366f1, #8b5cf6)'
                          : 'linear-gradient(135deg, #4b5563, #374151)',
                      boxShadow: saved
                        ? '0 0 20px rgba(16,185,129,0.3)'
                        : hasAtLeastOne
                          ? '0 0 20px rgba(99,102,241,0.3)'
                          : 'none',
                    }}
                  >
                    <AnimatePresence mode="wait">
                      {saved ? (
                        <motion.span key="saved" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center gap-2">
                          <Check className="h-4 w-4" /> Saved!
                        </motion.span>
                      ) : (
                        <motion.span key="save" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center gap-2">
                          <Key className="h-4 w-4" /> Save Configuration
                        </motion.span>
                      )}
                    </AnimatePresence>
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.97 }}
                    onClick={onClose}
                    className="rounded-xl border border-white/10 bg-white/5 px-6 py-3 text-sm font-semibold text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
                  >
                    Cancel
                  </motion.button>
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
