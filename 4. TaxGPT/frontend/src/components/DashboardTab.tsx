import { motion } from 'framer-motion'
import {
  Zap, Map, Users, FileText, ArrowLeftRight,
  Wallet, BookOpen, Layers, Calendar, Scale,
  Activity, Sparkles, ChevronRight,
} from 'lucide-react'
import { useHealth } from '../hooks/useHealth'
import { useApiKeyStore } from '../store/apiKeyStore'
import { TiltCard } from './TiltCard'

type TabType = 'dashboard' | 'mapper' | 'qa' | 'profile' | 'notice' | 'compare'

interface DashboardTabProps {
  onNavigate: (tab: TabType, query?: string) => void
  onOpenProvider: () => void
}

// ─── Provider meta ────────────────────────────────────────────────────────────

const PROVIDER_META: Record<string, { displayName: string; color: string; glow: string; defaultModel: string; logo: React.ReactNode }> = {
  gemini: {
    displayName: 'Google Gemini', color: 'text-blue-400', glow: '59,130,246', defaultModel: 'gemini-2.0-flash',
    logo: <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none"><path d="M12 2L9.5 9.5H2L8 13.5L5.5 21L12 17L18.5 21L16 13.5L22 9.5H14.5L12 2Z" fill="url(#g1)" /><defs><linearGradient id="g1" x1="2" y1="2" x2="22" y2="21"><stop offset="0%" stopColor="#4285F4" /><stop offset="100%" stopColor="#34A853" /></linearGradient></defs></svg>,
  },
  openai: {
    displayName: 'OpenAI', color: 'text-emerald-400', glow: '52,211,153', defaultModel: 'gpt-4o',
    logo: <svg viewBox="0 0 24 24" className="h-5 w-5 fill-emerald-400"><path d="M22.28 9.27a5.93 5.93 0 0 0-.51-4.89 6 6 0 0 0-6.44-2.87A5.93 5.93 0 0 0 10.84 0a6 6 0 0 0-5.72 4.16 5.93 5.93 0 0 0-3.96 2.87 6 6 0 0 0 .74 7.02 5.93 5.93 0 0 0 .51 4.89 6 6 0 0 0 6.44 2.87A5.93 5.93 0 0 0 13.16 24a6 6 0 0 0 5.72-4.16 5.93 5.93 0 0 0 3.96-2.87 6 6 0 0 0-.74-7.02zM13.16 22.5a4.5 4.5 0 0 1-2.89-1.05l.14-.08 4.8-2.77a.79.79 0 0 0 .4-.69v-6.77l2.03 1.17a.07.07 0 0 1 .04.06v5.6a4.5 4.5 0 0 1-4.52 4.53z" /></svg>,
  },
  anthropic: {
    displayName: 'Anthropic', color: 'text-orange-400', glow: '251,146,60', defaultModel: 'claude-opus-4-6',
    logo: <svg viewBox="0 0 24 24" className="h-5 w-5 fill-orange-400"><path d="M13.827 3.52h3.603L24 20h-3.603l-6.57-16.48zm-7.258 0h3.767L16.906 20h-3.674l-1.343-3.461H5.017L3.674 20H0L6.57 3.52zm4.132 9.959L8.453 7.687 6.205 13.48H10.7z" /></svg>,
  },
  openrouter: {
    displayName: 'OpenRouter', color: 'text-violet-400', glow: '167,139,250', defaultModel: 'openai/gpt-4o',
    logo: <div className="h-5 w-5 rounded bg-gradient-to-br from-violet-500 to-purple-700 flex items-center justify-center text-white text-[9px] font-black leading-none">OR</div>,
  },
  ollama: {
    displayName: 'Ollama', color: 'text-gray-300', glow: '209,213,219', defaultModel: 'llama3.1',
    logo: <div className="h-5 w-5 rounded-full bg-gradient-to-br from-gray-600 to-gray-800 border border-white/20 flex items-center justify-center text-white text-[9px] font-black">O</div>,
  },
}

const PROVIDER_SHORT: Record<string, string> = {
  gemini: 'Gemini', openai: 'GPT-4o', anthropic: 'Claude', openrouter: 'OpenRouter', ollama: 'Ollama',
}

// ─── Status cards ─────────────────────────────────────────────────────────────

function StatusCards({ onOpenProvider }: { onOpenProvider: () => void }) {
  const { data: health } = useHealth()
  const { provider, openrouterModel, ollamaModel } = useApiKeyStore()
  const meta = PROVIDER_META[provider] ?? PROVIDER_META.gemini
  const activeModel = provider === 'openrouter' ? openrouterModel : provider === 'ollama' ? ollamaModel : meta.defaultModel

  const cards = [
    {
      label: 'API Status',
      value: health?.status === 'healthy' ? 'Healthy' : 'Offline',
      sub: health?.status === 'healthy' ? 'All systems operational' : 'Check backend',
      dot: health?.status === 'healthy' ? 'bg-emerald-400 animate-pulse' : 'bg-red-400',
      glow: health?.status === 'healthy' ? '52,211,153' : '248,113,113',
      icon: <Activity className="h-5 w-5" style={{ color: health?.status === 'healthy' ? 'rgb(52,211,153)' : 'rgb(248,113,113)' }} />,
      onClick: undefined as (() => void) | undefined,
    },
    {
      label: 'Knowledge Index',
      value: health?.index_ready ? 'Ready' : 'Building',
      sub: health?.index_ready ? '536 sections indexed' : 'Ingestion in progress…',
      dot: health?.index_ready ? 'bg-sky-400' : 'bg-amber-400 animate-pulse',
      glow: health?.index_ready ? '56,189,248' : '251,191,36',
      icon: <Sparkles className="h-5 w-5" style={{ color: health?.index_ready ? 'rgb(56,189,248)' : 'rgb(251,191,36)' }} />,
      onClick: undefined as (() => void) | undefined,
    },
    {
      label: 'AI Provider',
      value: meta.displayName,
      sub: activeModel,
      dot: 'bg-violet-400 animate-pulse',
      glow: meta.glow,
      icon: meta.logo,
      onClick: onOpenProvider,
    },
  ]

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
      {cards.map((c, i) => (
        <motion.div key={c.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}>
          <TiltCard
            glowColor={c.glow} intensity={10}
            className={`bg-[#0d1117]/80 border border-white/8 backdrop-blur-2xl p-6 ${c.onClick ? 'cursor-pointer group' : ''}`}
            onClick={c.onClick}
          >
            <div className="absolute inset-0 rounded-2xl" style={{ background: `radial-gradient(circle at 30% 20%, rgba(${c.glow},0.06), transparent 60%)` }} />
            <div className="relative z-10">
              <div className="flex items-center justify-between mb-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/8" style={{ background: `rgba(${c.glow},0.12)` }}>
                  {c.icon}
                </div>
                <span className={`w-2.5 h-2.5 rounded-full ${c.dot}`} />
              </div>
              <p className="text-xs font-medium text-gray-500 uppercase tracking-widest mb-1">{c.label}</p>
              <p className="text-2xl font-bold mb-1" style={{ color: `rgb(${c.glow})` }}>{c.value}</p>
              <p className="text-xs text-gray-500 font-mono truncate">{c.sub}</p>
            </div>
          </TiltCard>
        </motion.div>
      ))}
    </div>
  )
}

// ─── Key changes ──────────────────────────────────────────────────────────────

const CHANGES = [
  { icon: Wallet,        color: '#a78bfa', label: 'Section 80C → Section 123',   sub: 'Deductions now under Chapter VI-A',          query: '80C' },
  { icon: BookOpen,      color: '#94a3b8', label: 'Assessment Year → Tax Year',   sub: 'Unified year terminology (Section 3)',        query: 'Assessment Year' },
  { icon: Layers,        color: '#38bdf8', label: 'Sections 192-194T → §393',     sub: 'All TDS consolidated into a single table',   query: 'TDS' },
  { icon: FileText,      color: '#6366f1', label: 'Section 139 → Section 263',    sub: 'Return filing deadlines preserved',           query: '139' },
  { icon: Calendar,      color: '#818cf8', label: 'Section 87A → Section 156',    sub: 'Tax rebate up to ₹12L income',               query: '87A' },
]

// ─── Feature grid ─────────────────────────────────────────────────────────────

const FEATURES: { icon: React.ComponentType<{ className?: string; style?: React.CSSProperties }>; color: string; label: string; desc: string; tab: TabType; badge?: string }[] = [
  { icon: Zap,            color: '#fbbf24', label: 'AI Assistant',     desc: 'Ask anything about the 2025 Act in plain English',  tab: 'qa' },
  { icon: Map,            color: '#a78bfa', label: 'Section Mapper',   desc: 'Map any old section to its new equivalent instantly', tab: 'mapper' },
  { icon: Users,          color: '#34d399', label: 'Profile Analysis', desc: 'Personalised tax impact by your taxpayer profile',  tab: 'profile' },
  { icon: FileText,       color: '#f87171', label: 'Notice Decoder',   desc: 'Decode and understand any tax notice or demand',    tab: 'notice' },
  { icon: ArrowLeftRight, color: '#38bdf8', label: 'Compare Acts',     desc: 'Side-by-side clause comparison: 1961 vs 2025',      tab: 'compare' },
]

// ─── Main component ───────────────────────────────────────────────────────────

export function DashboardTab({ onNavigate, onOpenProvider }: DashboardTabProps) {
  const { provider } = useApiKeyStore()
  const providerShort = PROVIDER_SHORT[provider] ?? 'AI'

  return (
    <div className="space-y-6 pb-6">
      <StatusCards onOpenProvider={onOpenProvider} />

      {/* Hero */}
      <TiltCard glowColor="99,102,241" intensity={6} className="border border-indigo-500/20 bg-[#0d1117]/70 backdrop-blur-2xl overflow-hidden">
        <div className="absolute inset-0 opacity-[0.03]"
          style={{ backgroundImage: 'linear-gradient(rgba(255,255,255,0.5) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,0.5) 1px,transparent 1px)', backgroundSize: '40px 40px' }} />
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-600/10 via-violet-600/5 to-transparent" />
        <div className="relative z-10 p-8 md:p-12">
          <div className="flex items-start gap-2 mb-4">
            <span className="flex h-2 w-2 rounded-full bg-emerald-400 animate-pulse mt-2" />
            <span className="text-xs font-medium text-emerald-400 uppercase tracking-widest">Income Tax Act 2025 · Effective 1 April 2026</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-black text-white leading-tight mb-4">
            India's Tax Law<br />
            <span className="bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">Changed Everything.</span>
          </h1>
          <p className="text-base text-white/50 max-w-xl leading-relaxed mb-8">
            The Income Tax Act 2025 replaced the 1961 Act — every section number, form number, and core terminology changed.
            TaxGPT helps you navigate the new Act with confidence.
          </p>
          <div className="flex flex-wrap gap-3">
            <motion.button
              whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}
              onClick={() => onNavigate('qa')}
              className="flex items-center gap-2 rounded-xl px-6 py-3 text-sm font-semibold text-white"
              style={{ background: 'linear-gradient(135deg,#6366f1,#8b5cf6)', boxShadow: '0 0 24px rgba(99,102,241,0.35)' }}
            >
              <Zap className="h-4 w-4" /> Ask TaxGPT
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}
              onClick={() => onNavigate('mapper')}
              className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-6 py-3 text-sm font-semibold hover:bg-white/10 transition-colors"
            >
              <Map className="h-4 w-4" /> Section Mapper
            </motion.button>
          </div>
        </div>
      </TiltCard>

      {/* Key Changes at a Glance */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-bold text-white/80">Key Changes at a Glance</h2>
          <button onClick={() => onNavigate('mapper')} className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 transition-colors">
            View all <ChevronRight className="h-3.5 w-3.5" />
          </button>
        </div>
        <div className="space-y-2">
          {CHANGES.map((c, i) => (
            <motion.button
              key={c.label}
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 + i * 0.05 }}
              whileHover={{ x: 4 }}
              onClick={() => onNavigate('mapper', c.query)}
              className="w-full flex items-center gap-4 rounded-xl border border-white/6 bg-white/[0.025] px-4 py-3.5 text-left hover:border-white/12 hover:bg-white/[0.04] transition-all group"
            >
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg" style={{ background: `${c.color}1a` }}>
                <c.icon className="h-4 w-4" style={{ color: c.color }} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-white/85 truncate">{c.label}</p>
                <p className="text-xs text-white/35 truncate mt-0.5">{c.sub}</p>
              </div>
              <ChevronRight className="h-4 w-4 text-white/20 group-hover:text-white/40 shrink-0 transition-colors" />
            </motion.button>
          ))}
        </div>
      </div>

      {/* Feature grid */}
      <div>
        <h2 className="text-base font-bold text-white/80 mb-4">What TaxGPT Can Do</h2>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
          {FEATURES.map((f, i) => (
            <motion.div
              key={f.label}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 + i * 0.06 }}
            >
              <TiltCard
                glowColor="99,102,241" intensity={8}
                className="bg-[#0d1117]/60 border border-white/7 backdrop-blur-xl p-5 cursor-pointer h-full"
                onClick={() => onNavigate(f.tab)}
              >
                <div className="relative z-10">
                  <div className="flex h-9 w-9 items-center justify-center rounded-xl mb-3" style={{ background: `${f.color}1a` }}>
                    <f.icon className="h-4 w-4" style={{ color: f.color }} />
                  </div>
                  <p className="text-sm font-semibold text-white/90 mb-1">{f.label}</p>
                  <p className="text-xs text-white/35 leading-snug">{f.desc}</p>
                  {f.label === 'AI Assistant' && (
                    <span className="mt-2 inline-block text-[10px] font-semibold px-1.5 py-0.5 rounded" style={{ background: `${f.color}18`, color: f.color }}>
                      RAG · {providerShort}
                    </span>
                  )}
                </div>
              </TiltCard>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}
