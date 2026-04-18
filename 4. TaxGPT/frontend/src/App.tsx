import { useState, useRef, useEffect } from 'react'
import { QueryClientProvider } from '@tanstack/react-query'
import { motion, AnimatePresence, useMotionValue, useSpring } from 'framer-motion'
import {
  BarChart3, FileText, Users, Bell,
  ArrowUpRight, ArrowDownRight, TrendingUp, TrendingDown,
  DollarSign, CheckCircle2, AlertCircle, Clock,
  Menu, Shield, Zap, Eye, EyeOff, Map, ChevronRight,
  Sparkles, Activity, ArrowLeftRight,
} from 'lucide-react'
import { queryClient } from './lib/queryClient'
import { useHealth } from './hooks/useHealth'
import { useApiKeyStore } from './store/apiKeyStore'
import { MapperTab } from './components/MapperTab'
import { CompareTab } from './components/CompareTab'
import { ParticleField } from './components/ParticleField'
import { TiltCard } from './components/TiltCard'
import { ProviderSelector } from './components/ProviderSelector'
import { AnimatedCounter } from './components/AnimatedCounter'

type TabType = 'dashboard' | 'mapper' | 'qa' | 'profile' | 'notice' | 'compare'
const cn = (...c: (string | boolean | undefined)[]) => c.filter(Boolean).join(' ')

// ─── Cursor glow that follows mouse ───────────────────────────────────────────
function CursorGlow() {
  const x = useMotionValue(0)
  const y = useMotionValue(0)
  const sx = useSpring(x, { stiffness: 80, damping: 20 })
  const sy = useSpring(y, { stiffness: 80, damping: 20 })

  useEffect(() => {
    const move = (e: MouseEvent) => { x.set(e.clientX); y.set(e.clientY) }
    window.addEventListener('mousemove', move)
    return () => window.removeEventListener('mousemove', move)
  }, [x, y])

  return (
    <motion.div
      className="fixed pointer-events-none z-50 mix-blend-screen"
      style={{
        left: sx, top: sy,
        width: 400, height: 400,
        x: '-50%', y: '-50%',
        background: 'radial-gradient(circle, rgba(99,102,241,0.12) 0%, transparent 70%)',
        borderRadius: '50%',
      }}
    />
  )
}

// ─── Aurora background blobs ───────────────────────────────────────────────────
function AuroraBackground() {
  return (
    <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
      <motion.div
        className="absolute rounded-full blur-3xl opacity-20"
        style={{ width: 700, height: 700, top: '-20%', left: '-15%', background: 'radial-gradient(circle, #4f46e5, #7c3aed)' }}
        animate={{ x: [0, 60, 0], y: [0, 40, 0], scale: [1, 1.1, 1] }}
        transition={{ duration: 18, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        className="absolute rounded-full blur-3xl opacity-15"
        style={{ width: 600, height: 600, bottom: '-20%', right: '-10%', background: 'radial-gradient(circle, #0ea5e9, #6366f1)' }}
        animate={{ x: [0, -50, 0], y: [0, -30, 0], scale: [1, 1.15, 1] }}
        transition={{ duration: 22, repeat: Infinity, ease: 'easeInOut', delay: 3 }}
      />
      <motion.div
        className="absolute rounded-full blur-3xl opacity-10"
        style={{ width: 400, height: 400, top: '40%', left: '50%', background: 'radial-gradient(circle, #8b5cf6, #06b6d4)' }}
        animate={{ x: [0, 30, -30, 0], y: [0, -40, 20, 0] }}
        transition={{ duration: 15, repeat: Infinity, ease: 'easeInOut', delay: 6 }}
      />
    </div>
  )
}

// ─── Floating ₹ coin with 3D rotation ─────────────────────────────────────────
function FloatingCoin() {
  return (
    <motion.div
      className="absolute right-8 top-8 pointer-events-none select-none hidden xl:flex"
      animate={{ y: [-10, 10, -10], rotateY: [0, 360] }}
      transition={{ y: { duration: 4, repeat: Infinity, ease: 'easeInOut' }, rotateY: { duration: 8, repeat: Infinity, ease: 'linear' } }}
      style={{ perspective: 400 }}
    >
      <div className="relative w-24 h-24">
        <div className="absolute inset-0 rounded-full bg-gradient-to-br from-yellow-400 via-amber-500 to-orange-500 shadow-[0_0_40px_rgba(251,191,36,0.4)] flex items-center justify-center text-4xl font-black text-white"
          style={{ boxShadow: '0 0 40px rgba(251,191,36,0.3), inset 0 2px 4px rgba(255,255,255,0.3)' }}>
          ₹
        </div>
        {/* Coin rim */}
        <div className="absolute inset-0 rounded-full border-4 border-yellow-300/30" />
      </div>
    </motion.div>
  )
}

// ─── Stat card with tilt + animated number ─────────────────────────────────────
function StatCard3D({
  title, value, change, icon: Icon, trend, glowColor, masked, prefix = '₹',
}: {
  title: string; value: number; change: string; icon: React.ComponentType<{ className?: string; style?: React.CSSProperties }>;
  trend: 'up' | 'down'; glowColor: string; masked?: boolean; prefix?: string
}) {
  const isUp = trend === 'up'
  return (
    <TiltCard glowColor={glowColor} className="bg-[#0d1117]/80 border border-white/8 backdrop-blur-2xl p-6">
      <div className="absolute inset-0 bg-gradient-to-br from-white/[0.03] to-transparent rounded-2xl" />
      <div className="relative z-20">
        <div className="flex items-center justify-between mb-5">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-white/10"
            style={{ background: `rgba(${glowColor}, 0.15)` }}>
            <Icon className="h-5 w-5" style={{ color: `rgb(${glowColor})` }} />
          </div>
          <span className={cn(
            'flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold',
            isUp ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400',
          )}>
            {isUp ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
            {change}
          </span>
        </div>
        <p className="text-xs font-medium text-gray-500 uppercase tracking-widest mb-1">{title}</p>
        <AnimatedCounter
          value={value}
          prefix={prefix === '₹' ? '₹' : ''}
          className="text-2xl font-bold text-white"
          masked={masked}
        />
      </div>
    </TiltCard>
  )
}

// ─── Dashboard tab ────────────────────────────────────────────────────────────
function DashboardTab({ showBalance, setShowBalance, onOpenProvider }: {
  showBalance: boolean; setShowBalance: (v: boolean) => void; onOpenProvider: () => void
}) {
  return (
    <div className="space-y-5">
      <StatusCards onOpenProvider={onOpenProvider} />
      <HeroCard showBalance={showBalance} setShowBalance={setShowBalance} />
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard3D title="Monthly Income" value={125000} change="+12.5%" icon={TrendingUp} trend="up" glowColor="56,189,248" masked={!showBalance} />
        <StatCard3D title="Deductions" value={28500} change="+8.2%" icon={TrendingDown} trend="up" glowColor="167,139,250" masked={!showBalance} />
        <StatCard3D title="Pending Returns" value={2} change="-50%" icon={FileText} trend="down" glowColor="248,113,113" prefix="" masked={false} />
        <StatCard3D title="Tax Saved" value={85000} change="+15.3%" icon={CheckCircle2} trend="up" glowColor="52,211,153" masked={!showBalance} />
      </div>
    </div>
  )
}

// ─── Hero metric card ─────────────────────────────────────────────────────────
function HeroCard({ showBalance, setShowBalance }: { showBalance: boolean; setShowBalance: (v: boolean) => void }) {
  const taxSummary = { totalIncome: 1850000, totalDeductions: 285000, taxableIncome: 1565000, estimatedTax: 312000, taxSaved: 85000 }

  return (
    <TiltCard
      glowColor="99, 102, 241"
      intensity={8}
      className="col-span-full border border-indigo-500/20 bg-[#0d1117]/70 backdrop-blur-2xl overflow-hidden"
    >
      {/* Grid lines */}
      <div className="absolute inset-0 opacity-[0.03]"
        style={{ backgroundImage: 'linear-gradient(rgba(255,255,255,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.5) 1px, transparent 1px)', backgroundSize: '40px 40px' }} />
      <div className="absolute inset-0 bg-gradient-to-br from-indigo-600/10 via-violet-600/5 to-transparent" />

      <FloatingCoin />

      <div className="relative z-10 p-8">
        <div className="flex flex-wrap items-start justify-between gap-6 mb-8">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="flex h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-xs font-medium text-emerald-400 uppercase tracking-widest">Live · FY 2025-26</span>
            </div>
            <p className="text-sm text-gray-400 mb-1">Total Tax Liability</p>
            <div className="flex items-center gap-3">
              <AnimatedCounter
                value={taxSummary.estimatedTax}
                prefix="₹"
                className="text-5xl font-black text-white tracking-tight"
                masked={!showBalance}
              />
              <button
                onClick={() => setShowBalance(!showBalance)}
                className="rounded-lg p-1.5 text-gray-500 hover:text-gray-300 hover:bg-white/5 transition-all"
              >
                {showBalance ? <Eye className="h-5 w-5" /> : <EyeOff className="h-5 w-5" />}
              </button>
            </div>
          </div>
          <div className="flex gap-3">
            <motion.button
              whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.97 }}
              className="rounded-xl px-6 py-3 text-sm font-semibold text-white"
              style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', boxShadow: '0 0 24px rgba(99,102,241,0.4)' }}
            >
              File Return
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.97 }}
              className="rounded-xl border border-white/10 bg-white/5 px-6 py-3 text-sm font-semibold backdrop-blur-sm hover:bg-white/10 transition-colors"
            >
              Download Report
            </motion.button>
          </div>
        </div>

        {/* Sub-metrics */}
        <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
          {[
            { label: 'Total Income', value: taxSummary.totalIncome, icon: TrendingUp, color: 'text-sky-400', border: 'border-sky-500/20', bg: 'bg-sky-500/5' },
            { label: 'Deductions', value: taxSummary.totalDeductions, icon: TrendingDown, color: 'text-violet-400', border: 'border-violet-500/20', bg: 'bg-violet-500/5' },
            { label: 'Taxable Income', value: taxSummary.taxableIncome, icon: DollarSign, color: 'text-amber-400', border: 'border-amber-500/20', bg: 'bg-amber-500/5' },
            { label: 'Tax Saved', value: taxSummary.taxSaved, icon: CheckCircle2, color: 'text-emerald-400', border: 'border-emerald-500/20', bg: 'bg-emerald-500/5' },
          ].map((m) => (
            <motion.div
              key={m.label}
              whileHover={{ y: -2 }}
              className={cn('rounded-xl border p-4', m.border, m.bg, 'backdrop-blur-sm')}
            >
              <div className="flex items-center gap-2 mb-2">
                <m.icon className={cn('h-4 w-4', m.color)} />
                <p className="text-xs text-gray-500 uppercase tracking-wider">{m.label}</p>
              </div>
              <AnimatedCounter value={m.value} prefix="₹" className={cn('text-lg font-bold', m.color)} masked={!showBalance} />
            </motion.div>
          ))}
        </div>
      </div>
    </TiltCard>
  )
}

const PROVIDER_META: Record<string, { displayName: string; color: string; glow: string; defaultModel: string; logo: React.ReactNode }> = {
  gemini: {
    displayName: 'Google Gemini',
    color: 'text-blue-400', glow: '59,130,246', defaultModel: 'gemini-2.0-flash',
    logo: (
      <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none">
        <path d="M12 2L9.5 9.5H2L8 13.5L5.5 21L12 17L18.5 21L16 13.5L22 9.5H14.5L12 2Z" fill="url(#g1)" />
        <defs><linearGradient id="g1" x1="2" y1="2" x2="22" y2="21"><stop offset="0%" stopColor="#4285F4" /><stop offset="100%" stopColor="#34A853" /></linearGradient></defs>
      </svg>
    ),
  },
  openai: {
    displayName: 'OpenAI',
    color: 'text-emerald-400', glow: '52,211,153', defaultModel: 'gpt-4o',
    logo: (
      <svg viewBox="0 0 24 24" className="h-5 w-5 fill-emerald-400">
        <path d="M22.28 9.27a5.93 5.93 0 0 0-.51-4.89 6 6 0 0 0-6.44-2.87A5.93 5.93 0 0 0 10.84 0a6 6 0 0 0-5.72 4.16 5.93 5.93 0 0 0-3.96 2.87 6 6 0 0 0 .74 7.02 5.93 5.93 0 0 0 .51 4.89 6 6 0 0 0 6.44 2.87A5.93 5.93 0 0 0 13.16 24a6 6 0 0 0 5.72-4.16 5.93 5.93 0 0 0 3.96-2.87 6 6 0 0 0-.74-7.02zM13.16 22.5a4.5 4.5 0 0 1-2.89-1.05l.14-.08 4.8-2.77a.79.79 0 0 0 .4-.69v-6.77l2.03 1.17a.07.07 0 0 1 .04.06v5.6a4.5 4.5 0 0 1-4.52 4.53zM3.54 18.38A4.5 4.5 0 0 1 3 15.83v-.14l4.87 2.81-.01-.14-.01 5.55a.78.78 0 0 0 .4.68l5.85 3.38L9.17 17.4a.08.08 0 0 1-.07 0L4.2 14.56a4.5 4.5 0 0 1-1.59-6.08l-.01-.01zm-.93-9.9a4.5 4.5 0 0 1 2.35-1.98v5.71a.78.78 0 0 0 .4.68l5.85 3.38L9.17 17.4a.08.08 0 0 1-.07 0L4.2 14.56a4.5 4.5 0 0 1-1.59-6.08zm16.62 3.86-5.85-3.38 2.03-1.17a.08.08 0 0 1 .07 0l4.9 2.83a4.49 4.49 0 0 1-.7 8.1v-5.7a.77.77 0 0 0-.4-.68zm2.02-3.02-.07-.04-4.8-2.77a.79.79 0 0 0-.8 0L9.73 9.9V7.56a.08.08 0 0 1 .03-.07l4.88-2.82a4.5 4.5 0 0 1 6.61 4.67zm-12.7 4.17-2.04-1.17a.08.08 0 0 1-.04-.07V6.66a4.5 4.5 0 0 1 7.38-3.45l-.14.08L9.91 6.06a.78.78 0 0 0-.4.68v6.75l-2.03-1.17-.03.02zm1.1-2.37 2.61-1.5 2.6 1.5v3l-2.6 1.5-2.6-1.5V11.1z" />
      </svg>
    ),
  },
  anthropic: {
    displayName: 'Anthropic',
    color: 'text-orange-400', glow: '251,146,60', defaultModel: 'claude-opus-4-6',
    logo: (
      <svg viewBox="0 0 24 24" className="h-5 w-5 fill-orange-400">
        <path d="M13.827 3.52h3.603L24 20h-3.603l-6.57-16.48zm-7.258 0h3.767L16.906 20h-3.674l-1.343-3.461H5.017L3.674 20H0L6.57 3.52zm4.132 9.959L8.453 7.687 6.205 13.48H10.7z" />
      </svg>
    ),
  },
  openrouter: {
    displayName: 'OpenRouter',
    color: 'text-violet-400', glow: '167,139,250', defaultModel: 'openai/gpt-4o',
    logo: (
      <div className="h-5 w-5 rounded bg-gradient-to-br from-violet-500 to-purple-700 flex items-center justify-center text-white text-[9px] font-black leading-none">OR</div>
    ),
  },
  ollama: {
    displayName: 'Ollama',
    color: 'text-gray-300', glow: '209,213,219', defaultModel: 'llama3.1',
    logo: (
      <div className="h-5 w-5 rounded-full bg-gradient-to-br from-gray-600 to-gray-800 border border-white/20 flex items-center justify-center text-white text-[9px] font-black">O</div>
    ),
  },
}

// ─── System status cards ──────────────────────────────────────────────────────
function StatusCards({ onOpenProvider }: { onOpenProvider: () => void }) {
  const { data: health } = useHealth()
  const { provider, openrouterModel, ollamaModel } = useApiKeyStore()
  const meta = PROVIDER_META[provider] ?? PROVIDER_META.gemini
  const activeModel =
    provider === 'openrouter' ? openrouterModel :
    provider === 'ollama' ? ollamaModel :
    meta.defaultModel

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
      {/* API Status */}
      {[0, 1, 2].map((i) => {
        const isProvider = i === 2
        const label = i === 0 ? 'API Status' : i === 1 ? 'Knowledge Index' : 'AI Provider'
        const value = i === 0
          ? (health?.status === 'healthy' ? 'Healthy' : 'Offline')
          : i === 1
          ? (health?.index_ready ? 'Ready' : 'Building')
          : meta.displayName
        const sub = i === 0
          ? (health?.status === 'healthy' ? 'All systems operational' : 'Check backend')
          : i === 1
          ? (health?.index_ready ? '536 sections indexed' : 'Ingestion in progress…')
          : activeModel
        const dot = i === 0
          ? (health?.status === 'healthy' ? 'bg-emerald-400 animate-pulse' : 'bg-red-400')
          : i === 1
          ? (health?.index_ready ? 'bg-sky-400' : 'bg-amber-400 animate-pulse')
          : 'bg-violet-400 animate-pulse'
        const glow = i === 0
          ? (health?.status === 'healthy' ? '52,211,153' : '248,113,113')
          : i === 1
          ? (health?.index_ready ? '56,189,248' : '251,191,36')
          : meta.glow
        const Icon = i === 0 ? Activity : i === 1 ? Sparkles : null

        return (
          <motion.div
            key={label}
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
          >
            <TiltCard
              glowColor={glow}
              intensity={10}
              className={cn('bg-[#0d1117]/80 border border-white/8 backdrop-blur-2xl p-6', isProvider && 'cursor-pointer group')}
            >
              <div className="absolute inset-0 rounded-2xl" style={{ background: `radial-gradient(circle at 30% 20%, rgba(${glow}, 0.06), transparent 60%)` }} />
              {isProvider && (
                <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                  style={{ background: `radial-gradient(circle at 50% 50%, rgba(${glow}, 0.07), transparent 70%)` }} />
              )}

              <div className="relative z-10" onClick={isProvider ? onOpenProvider : undefined}>
                {/* Absolutely-positioned overlay — zero layout impact */}
                {isProvider && (
                  <div className="absolute top-6 right-6 z-20 flex flex-col items-end gap-1 pointer-events-none">
                    <span className="text-[10px] font-semibold uppercase tracking-widest text-gray-600 group-hover:text-gray-400 transition-colors">
                      Change
                    </span>
                    <span
                      className="flex items-center gap-1 text-[10px] font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                      style={{ color: `rgb(${glow})` }}
                    >
                      <Sparkles className="h-2.5 w-2.5 shrink-0" />
                      Switch model
                    </span>
                  </div>
                )}

                {/* Icon row — identical height for all three cards */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/8"
                    style={{ background: `rgba(${glow}, 0.12)` }}>
                    {isProvider
                      ? meta.logo
                      : Icon && <Icon className="h-5 w-5" style={{ color: `rgb(${glow})` }} />}
                  </div>
                  <span className={cn('w-2.5 h-2.5 rounded-full', dot)} />
                </div>

                {/* Text — identical structure for all three */}
                <p className="text-xs font-medium text-gray-500 uppercase tracking-widest mb-1">{label}</p>
                <p className="text-2xl font-bold mb-1" style={{ color: `rgb(${glow})` }}>{value}</p>
                <p className="text-xs text-gray-500 font-mono truncate">{sub}</p>
              </div>
            </TiltCard>
          </motion.div>
        )
      })}
    </div>
  )
}

// ─── Notifications ────────────────────────────────────────────────────────────
const INITIAL_NOTIFS = [
  { id: '1', title: 'Tax Filing Deadline', message: 'Approaching in 15 days', time: '2h ago', read: false, type: 'warning' as const },
  { id: '2', title: 'Deduction Approved', message: 'Business expense deduction approved', time: '5h ago', read: false, type: 'success' as const },
  { id: '3', title: 'New Tax Update', message: 'FY 2025-26 regulations published', time: '1d ago', read: true, type: 'info' as const },
]

// ─── Coming soon placeholder ──────────────────────────────────────────────────
function ComingSoon({ label, icon: Icon }: { label: string; icon: React.ComponentType<{ className?: string; style?: React.CSSProperties }> }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.97 }}
      animate={{ opacity: 1, scale: 1 }}
      className="flex flex-col items-center justify-center min-h-96 rounded-2xl border border-white/8 bg-[#0d1117]/60 backdrop-blur-2xl text-center"
    >
      <motion.div
        animate={{ y: [-6, 6, -6] }}
        transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
        className="mb-6 flex h-20 w-20 items-center justify-center rounded-2xl border border-indigo-500/20 bg-gradient-to-br from-indigo-500/10 to-violet-500/10"
      >
        <Icon className="h-10 w-10 text-indigo-400" />
      </motion.div>
      <h3 className="text-xl font-bold text-white mb-2">{label}</h3>
      <p className="text-gray-500 text-sm">This feature is coming soon.</p>
      <motion.div
        className="mt-6 h-1 w-24 rounded-full bg-gradient-to-r from-indigo-500 to-violet-500"
        animate={{ scaleX: [0.5, 1, 0.5], opacity: [0.5, 1, 0.5] }}
        transition={{ duration: 2, repeat: Infinity }}
      />
    </motion.div>
  )
}

// ─── Main app ─────────────────────────────────────────────────────────────────
function AppContent() {
  const [activeTab, setActiveTab] = useState<TabType>('dashboard')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [showNotifications, setShowNotifications] = useState(false)
  const [showBalance, setShowBalance] = useState(true)
  const [providerOpen, setProviderOpen] = useState(false)
  const [notifs, setNotifs] = useState(INITIAL_NOTIFS)
  const notifRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const h = (e: MouseEvent) => {
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) setShowNotifications(false)
    }
    document.addEventListener('mousedown', h)
    return () => document.removeEventListener('mousedown', h)
  }, [])

  const unread = notifs.filter((n) => !n.read).length

  const nav: { id: TabType; icon: React.ComponentType<{ className?: string; style?: React.CSSProperties }>; label: string; badge?: string }[] = [
    { id: 'dashboard', icon: BarChart3, label: 'Dashboard' },
    { id: 'mapper', icon: Map, label: 'Section Mapper', badge: 'Live' },
    { id: 'qa', icon: Zap, label: 'AI Assistant', badge: 'Soon' },
    { id: 'profile', icon: Users, label: 'Profile Analysis', badge: 'Soon' },
    { id: 'notice', icon: FileText, label: 'Notice Decoder', badge: 'Soon' },
    { id: 'compare', icon: ArrowLeftRight, label: 'Compare Acts', badge: 'New' },
  ]

  const pageTitle: Record<TabType, string> = {
    dashboard: 'Dashboard', mapper: 'Section Mapper',
    qa: 'AI Assistant', profile: 'Profile Analysis', notice: 'Notice Decoder',
    compare: 'Compare Acts',
  }

  return (
    <div className="min-h-screen text-white" style={{ background: '#070b14' }}>
      <AuroraBackground />
      <ParticleField />
      <CursorGlow />

      {/* ── Sidebar ── */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.aside
            initial={{ x: -280, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -280, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 300, damping: 35 }}
            className="fixed left-0 top-0 z-40 h-screen w-64"
            style={{ background: 'rgba(7,11,20,0.9)', borderRight: '1px solid rgba(255,255,255,0.06)', backdropFilter: 'blur(24px)' }}
          >
            {/* Sidebar glow */}
            <div className="absolute inset-y-0 right-0 w-px bg-gradient-to-b from-transparent via-indigo-500/30 to-transparent" />

            <div className="flex h-full flex-col p-5">
              {/* Logo */}
              <motion.div className="mb-8 flex items-center gap-3" whileHover={{ x: 2 }}>
                <div className="flex h-10 w-10 items-center justify-center rounded-xl text-lg font-black text-white"
                  style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', boxShadow: '0 0 20px rgba(99,102,241,0.4)' }}>
                  ₹
                </div>
                <div>
                  <h1 className="text-lg font-black tracking-tight">TaxGPT</h1>
                  <p className="text-[10px] font-medium text-gray-500 uppercase tracking-widest">India · 2025 Act</p>
                </div>
              </motion.div>

              {/* Nav items */}
              <nav className="flex-1 space-y-1">
                {nav.map((item) => {
                  const active = activeTab === item.id
                  return (
                    <motion.button
                      key={item.id}
                      onClick={() => setActiveTab(item.id)}
                      whileHover={{ x: 4 }}
                      whileTap={{ scale: 0.97 }}
                      className={cn(
                        'relative flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-colors',
                        active ? 'text-white' : 'text-gray-500 hover:text-gray-300',
                      )}
                    >
                      {active && (
                        <motion.div
                          layoutId="activeNav"
                          className="absolute inset-0 rounded-xl"
                          style={{ background: 'linear-gradient(135deg, rgba(99,102,241,0.2), rgba(139,92,246,0.15))', border: '1px solid rgba(99,102,241,0.3)' }}
                          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                        />
                      )}
                      <item.icon className={cn('relative z-10 h-4 w-4 shrink-0', active ? 'text-indigo-400' : '')} />
                      <span className="relative z-10 flex-1 text-left">{item.label}</span>
                      {item.badge && (
                        <span className={cn(
                          'relative z-10 rounded-full px-1.5 py-0.5 text-[10px] font-semibold',
                          item.badge === 'Live' ? 'bg-emerald-500/15 text-emerald-400' :
                          item.badge === 'New' ? 'bg-indigo-500/20 text-indigo-400' :
                          'bg-white/5 text-gray-500',
                        )}>{item.badge}</span>
                      )}
                    </motion.button>
                  )
                })}
              </nav>

              {/* AI CTA */}
              <motion.div
                whileHover={{ scale: 1.02 }}
                className="rounded-xl p-4 border border-indigo-500/20 cursor-pointer"
                style={{ background: 'linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.08))' }}
                onClick={() => setActiveTab('qa')}
              >
                <div className="flex items-center gap-2 mb-2">
                  <Zap className="h-4 w-4 text-amber-400" />
                  <span className="text-sm font-semibold">AI Assistant</span>
                </div>
                <p className="text-xs text-gray-500 mb-3 leading-relaxed">Instant answers on new Income Tax Act 2025</p>
                <div className="flex w-full items-center justify-center gap-2 rounded-lg py-2.5 text-sm font-semibold text-white"
                  style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', boxShadow: '0 0 16px rgba(99,102,241,0.3)' }}>
                  Ask TaxGPT
                  <ChevronRight className="h-4 w-4" />
                </div>
              </motion.div>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* ── Main ── */}
      <motion.div
        animate={{ marginLeft: sidebarOpen ? 256 : 0 }}
        transition={{ type: 'spring', stiffness: 300, damping: 35 }}
      >
        {/* Header */}
        <header className="sticky top-0 z-30 px-6 py-4" style={{ background: 'rgba(7,11,20,0.85)', borderBottom: '1px solid rgba(255,255,255,0.06)', backdropFilter: 'blur(24px)' }}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <motion.button
                whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="rounded-lg p-2 text-gray-400 hover:bg-white/5 hover:text-white transition-all"
              >
                <Menu className="h-5 w-5" />
              </motion.button>
              <div>
                <h2 className="text-lg font-bold">{pageTitle[activeTab]}</h2>
                <p className="text-[11px] text-gray-500">Income Tax Act 2025 · India</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {/* Notifications */}
              <div className="relative" ref={notifRef}>
                <motion.button
                  whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                  onClick={() => setShowNotifications(!showNotifications)}
                  className="relative rounded-xl border border-white/8 bg-white/[0.03] p-2.5 hover:bg-white/8 transition-all"
                >
                  <Bell className="h-4 w-4 text-gray-400" />
                  {unread > 0 && (
                    <motion.span
                      initial={{ scale: 0 }} animate={{ scale: 1 }}
                      className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold"
                    >{unread}</motion.span>
                  )}
                </motion.button>

                <AnimatePresence>
                  {showNotifications && (
                    <motion.div
                      initial={{ opacity: 0, y: 8, scale: 0.96 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: 8, scale: 0.96 }}
                      transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                      className="absolute right-0 top-full mt-2 w-80 rounded-2xl border border-white/8 z-50 overflow-hidden"
                      style={{ background: 'rgba(10,14,26,0.98)', backdropFilter: 'blur(24px)' }}
                    >
                      {/* Header */}
                      <div className="flex items-center justify-between px-4 py-3 border-b border-white/8">
                        <div className="flex items-center gap-2">
                          <h3 className="font-semibold text-sm">Notifications</h3>
                          {unread > 0 && (
                            <span className="flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold">
                              {unread}
                            </span>
                          )}
                        </div>
                        {notifs.length > 0 && (
                          <motion.button
                            whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                            onClick={() => setNotifs([])}
                            className="text-[11px] font-medium text-gray-500 hover:text-red-400 transition-colors"
                          >
                            Clear all
                          </motion.button>
                        )}
                      </div>

                      {/* Body */}
                      <div className="p-3 space-y-2">
                        <AnimatePresence>
                          {notifs.length === 0 ? (
                            <motion.div
                              key="empty"
                              initial={{ opacity: 0 }}
                              animate={{ opacity: 1 }}
                              className="flex flex-col items-center justify-center py-8 gap-2"
                            >
                              <Bell className="h-8 w-8 text-gray-700" />
                              <p className="text-xs text-gray-600">No notifications</p>
                            </motion.div>
                          ) : (
                            notifs.map((n) => (
                              <motion.div
                                key={n.id}
                                layout
                                initial={{ opacity: 0, x: 10 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: 20, transition: { duration: 0.15 } }}
                                whileHover={{ x: 2 }}
                                className={cn('rounded-xl border p-3 cursor-pointer transition-colors',
                                  n.read ? 'border-white/5 bg-white/[0.02]' : 'border-indigo-500/20 bg-indigo-500/5')}
                              >
                                <div className="flex items-start justify-between gap-2 mb-1">
                                  <p className="text-sm font-medium">{n.title}</p>
                                  {n.type === 'warning' && <AlertCircle className="h-3.5 w-3.5 text-amber-400 shrink-0" />}
                                  {n.type === 'success' && <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 shrink-0" />}
                                  {n.type === 'info' && <Clock className="h-3.5 w-3.5 text-sky-400 shrink-0" />}
                                </div>
                                <p className="text-xs text-gray-500">{n.message}</p>
                                <p className="text-[10px] text-gray-600 mt-1">{n.time}</p>
                              </motion.div>
                            ))
                          )}
                        </AnimatePresence>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {/* Shield */}
              <div className="flex items-center gap-1.5 rounded-xl border border-white/8 bg-white/[0.03] px-3 py-2 text-xs text-gray-500">
                <Shield className="h-3.5 w-3.5 text-indigo-400" />
                Secured
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-6 min-h-screen">
          <AnimatePresence mode="wait">
            {activeTab === 'dashboard' && (
              <motion.div
                key="dashboard"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.3 }}
              >
                <DashboardTab
                  showBalance={showBalance}
                  setShowBalance={setShowBalance}
                  onOpenProvider={() => setProviderOpen(true)}
                />
              </motion.div>
            )}

            {activeTab === 'mapper' && (
              <motion.div key="mapper" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                <div className="rounded-2xl border border-white/8 bg-[#0d1117]/70 backdrop-blur-2xl p-8">
                  <MapperTab />
                </div>
              </motion.div>
            )}

            {activeTab === 'qa' && (
              <motion.div key="qa" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                <ComingSoon label="AI Assistant" icon={Zap} />
              </motion.div>
            )}
            {activeTab === 'profile' && (
              <motion.div key="profile" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                <ComingSoon label="Profile Analysis" icon={Users} />
              </motion.div>
            )}
            {activeTab === 'notice' && (
              <motion.div key="notice" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                <ComingSoon label="Notice Decoder" icon={FileText} />
              </motion.div>
            )}
            {activeTab === 'compare' && (
              <motion.div
                key="compare"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                style={{ height: 'calc(100vh - 120px)' }}
              >
                <CompareTab />
              </motion.div>
            )}
          </AnimatePresence>
        </main>
      </motion.div>

      <ProviderSelector open={providerOpen} onClose={() => setProviderOpen(false)} />
    </div>
  )
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  )
}
