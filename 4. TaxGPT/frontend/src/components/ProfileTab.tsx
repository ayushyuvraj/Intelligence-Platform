import { useState } from 'react'
import { motion } from 'framer-motion'
import { Loader, AlertCircle, CheckCircle2, Key } from 'lucide-react'
import { useProfiles, useProfileAnalysis } from '../hooks/useProfile'
import { useApiKeyStore } from '../store/apiKeyStore'

const PROFILE_ICONS = {
  salaried: '👔',
  business: '📊',
  investor: '📈',
  nri: '✈️',
  freelancer: '💼',
}

interface ProfileTabProps {
  onOpenSettings?: () => void
}

export function ProfileTab({ onOpenSettings }: ProfileTabProps) {
  const [selectedProfile, setSelectedProfile] = useState<string | null>(null)
  const { data: profilesData } = useProfiles()
  const { mutate, isPending, data: analysisData, error } = useProfileAnalysis()
  const { provider, geminiKey, anthropicKey, openaiKey, openrouterKey, ollamaUrl } = useApiKeyStore()

  const apiKey =
    provider === 'gemini' ? geminiKey :
    provider === 'anthropic' ? anthropicKey :
    provider === 'openai' ? openaiKey :
    provider === 'openrouter' ? openrouterKey :
    provider === 'ollama' ? ollamaUrl : ''

  const handleAnalyze = (profileId: string) => {
    if (!apiKey) return
    setSelectedProfile(profileId)
    mutate(profileId)
  }

  if (!apiKey) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex flex-col items-center justify-center min-h-96 rounded-2xl border border-amber-500/20 bg-amber-500/5 backdrop-blur-2xl text-center p-8"
      >
        <AlertCircle className="h-12 w-12 text-amber-400 mb-4" />
        <h3 className="text-xl font-bold text-white mb-2">API Key Required</h3>
        <p className="text-gray-400 text-sm mb-6">
          Configure at least one AI provider to use profile analysis
        </p>
        {onOpenSettings && (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onOpenSettings}
            className="flex items-center gap-2 rounded-lg px-6 py-3 text-sm font-semibold text-white bg-gradient-to-r from-indigo-600 to-violet-600 hover:shadow-lg hover:shadow-indigo-500/30 transition-all"
          >
            <Key className="h-4 w-4" />
            Configure Providers
          </motion.button>
        )}
      </motion.div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Profile Selection Grid */}
      <div>
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Select Your Profile</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
          {profilesData?.profiles.map((profile) => (
            <motion.button
              key={profile.id}
              whileHover={{ y: -2 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => handleAnalyze(profile.id)}
              disabled={isPending}
              className={`rounded-xl border p-4 text-center transition-all ${
                selectedProfile === profile.id
                  ? 'border-indigo-500 bg-indigo-500/15 text-white'
                  : 'border-white/10 bg-white/5 text-gray-300 hover:border-white/20 hover:bg-white/8'
              } ${isPending ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <div className="text-2xl mb-2">{PROFILE_ICONS[profile.id as keyof typeof PROFILE_ICONS]}</div>
              <p className="text-xs font-medium">{profile.label}</p>
            </motion.button>
          ))}
        </div>
      </div>

      {/* Analysis Result */}
      {isPending && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col items-center justify-center min-h-96 rounded-2xl border border-white/8 bg-[#0d1117]/70 backdrop-blur-2xl"
        >
          <Loader className="h-8 w-8 animate-spin text-indigo-400 mb-4" />
          <p className="text-gray-400">Analyzing profile...</p>
        </motion.div>
      )}

      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl p-4 flex gap-3"
        >
          <AlertCircle className="h-5 w-5 shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-sm">Analysis Failed</p>
            <p className="text-xs mt-1">{error.message}</p>
          </div>
        </motion.div>
      )}

      {analysisData && !isPending && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-2xl border border-indigo-500/20 bg-gradient-to-br from-indigo-500/10 to-violet-500/10 backdrop-blur-2xl p-8"
        >
          <div className="flex items-start gap-4 mb-6">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl border border-indigo-500/30 bg-indigo-500/20">
              <CheckCircle2 className="h-6 w-6 text-indigo-400" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-white">{analysisData.label}</h3>
              <p className="text-sm text-gray-400">Tax Impact Analysis</p>
            </div>
          </div>

          <div className="prose prose-invert max-w-none">
            <p className="text-gray-200 whitespace-pre-wrap text-sm leading-relaxed">
              {analysisData.analysis}
            </p>
          </div>

          {analysisData.source && (
            <div className="mt-6 pt-6 border-t border-white/10">
              <p className="text-xs text-gray-500">
                <span className="font-semibold">Source:</span> {analysisData.source}
              </p>
            </div>
          )}
        </motion.div>
      )}

      {!isPending && !analysisData && !error && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col items-center justify-center min-h-96 rounded-2xl border border-white/8 bg-[#0d1117]/70 backdrop-blur-2xl text-center"
        >
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl border border-indigo-500/20 bg-indigo-500/10 mb-4">
            <span className="text-3xl">📋</span>
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">Profile Analysis</h3>
          <p className="text-gray-500 text-sm max-w-xs">
            Select your taxpayer profile to get personalized tax impact analysis for the new Income Tax Act 2025
          </p>
        </motion.div>
      )}
    </div>
  )
}
