import { useState, useRef, useEffect } from 'react'
import { QueryClientProvider } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search, BarChart3, FileText, Users,
  Bell, ArrowUpRight, ArrowDownRight,
  TrendingUp, TrendingDown, DollarSign, CheckCircle2,
  AlertCircle, Clock, Menu, Shield, Zap, Eye, EyeOff,
  Map,
} from 'lucide-react'
import { queryClient } from './lib/queryClient'
import { useHealth } from './hooks/useHealth'
import { MapperTab } from './components/MapperTab'

type TabType = 'dashboard' | 'mapper' | 'qa' | 'profile' | 'notice'

const cn = (...classes: (string | boolean | undefined)[]) => classes.filter(Boolean).join(' ')

// Stat card used on the dashboard tab
function StatCard({
  title, value, change, icon: Icon, trend,
}: {
  title: string; value: string; change: string; icon: React.ComponentType<{ className?: string }>; trend: 'up' | 'down'
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-br from-white/5 to-white/[0.02] p-6 backdrop-blur-xl"
    >
      <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-purple-500/5 to-transparent opacity-50" />
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 backdrop-blur-sm">
            <Icon className="h-6 w-6 text-blue-400" />
          </div>
          <div className={cn(
            'flex items-center gap-1 rounded-full px-2 py-1 text-xs font-medium',
            trend === 'up' ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400',
          )}>
            {trend === 'up' ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
            {change}
          </div>
        </div>
        <p className="text-sm text-gray-400 mb-1">{title}</p>
        <p className="text-2xl font-bold text-white">{value}</p>
      </div>
    </motion.div>
  )
}

const mockNotifications = [
  { id: '1', title: 'Tax Filing Deadline', message: 'Your deadline is approaching in 15 days', time: '2 hours ago', read: false, type: 'warning' as const },
  { id: '2', title: 'Deduction Approved', message: 'Your business expense deduction has been approved', time: '5 hours ago', read: false, type: 'success' as const },
  { id: '3', title: 'New Tax Update', message: 'New regulations for FY 2025-26 are now available', time: '1 day ago', read: true, type: 'info' as const },
]

const taxSummary = {
  totalIncome: 1850000,
  totalDeductions: 285000,
  taxableIncome: 1565000,
  estimatedTax: 312000,
  taxSaved: 85000,
}

// Dashboard status tab — uses the 21st.dev design
function DashboardTab({ showBalance, setShowBalance }: { showBalance: boolean; setShowBalance: (v: boolean) => void }) {
  const { data: health } = useHealth()
  const fmt = (n: number) => showBalance ? `₹${n.toLocaleString('en-IN')}` : '₹••••••'

  return (
    <div className="space-y-6">
      {/* Live System Status */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {[
          {
            label: 'API Status',
            value: health?.status === 'healthy' ? 'Live' : 'Offline',
            color: health?.status === 'healthy' ? 'text-green-400' : 'text-red-400',
            bg: health?.status === 'healthy' ? 'bg-green-500/10 border-green-500/20' : 'bg-red-500/10 border-red-500/20',
            dot: health?.status === 'healthy' ? 'bg-green-400' : 'bg-red-400',
          },
          {
            label: 'Knowledge Index',
            value: health?.index_ready ? 'Ready' : 'Building…',
            color: health?.index_ready ? 'text-blue-400' : 'text-yellow-400',
            bg: health?.index_ready ? 'bg-blue-500/10 border-blue-500/20' : 'bg-yellow-500/10 border-yellow-500/20',
            dot: health?.index_ready ? 'bg-blue-400' : 'bg-yellow-400 animate-pulse',
          },
          {
            label: 'AI Provider',
            value: health?.provider ? health.provider.charAt(0).toUpperCase() + health.provider.slice(1) : '—',
            color: 'text-purple-400',
            bg: 'bg-purple-500/10 border-purple-500/20',
            dot: 'bg-purple-400',
          },
        ].map((item) => (
          <motion.div
            key={item.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={cn('relative overflow-hidden rounded-2xl border p-6 backdrop-blur-xl', item.bg)}
          >
            <div className="flex items-center gap-2 mb-3">
              <span className={cn('w-2 h-2 rounded-full', item.dot)} />
              <p className="text-sm text-gray-400">{item.label}</p>
            </div>
            <p className={cn('text-3xl font-bold', item.color)}>{item.value}</p>
          </motion.div>
        ))}
      </div>

      {/* Tax Summary Hero Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-br from-blue-500/10 via-purple-500/10 to-transparent p-8 backdrop-blur-xl"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5" />
        <div className="relative z-10">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-400">Total Tax Liability (FY 2025-26)</h3>
              <div className="mt-2 flex items-center gap-4">
                <p className="text-4xl font-bold">{fmt(taxSummary.estimatedTax)}</p>
                <button onClick={() => setShowBalance(!showBalance)} className="rounded-lg p-2 hover:bg-white/5 transition-colors">
                  {showBalance ? <Eye className="h-5 w-5 text-gray-400" /> : <EyeOff className="h-5 w-5 text-gray-400" />}
                </button>
              </div>
            </div>
            <div className="flex gap-2">
              <button className="rounded-xl bg-gradient-to-r from-blue-500 to-purple-600 px-6 py-3 font-medium transition-transform hover:scale-105 text-sm">
                File Return
              </button>
              <button className="rounded-xl border border-white/10 bg-white/5 px-6 py-3 font-medium backdrop-blur-sm hover:bg-white/10 transition-colors text-sm">
                Download Report
              </button>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            {[
              { label: 'Total Income', value: fmt(taxSummary.totalIncome), icon: TrendingUp },
              { label: 'Deductions', value: fmt(taxSummary.totalDeductions), icon: TrendingDown },
              { label: 'Taxable Income', value: fmt(taxSummary.taxableIncome), icon: DollarSign },
              { label: 'Tax Saved', value: fmt(taxSummary.taxSaved), icon: CheckCircle2 },
            ].map((item) => (
              <div key={item.label} className="rounded-xl border border-white/10 bg-white/5 p-4 backdrop-blur-sm">
                <div className="mb-2 flex items-center gap-2">
                  <item.icon className="h-4 w-4 text-gray-400" />
                  <p className="text-sm text-gray-400">{item.label}</p>
                </div>
                <p className="text-xl font-bold">{item.value}</p>
              </div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
        <StatCard title="Monthly Income" value={fmt(125000)} change="+12.5%" icon={TrendingUp} trend="up" />
        <StatCard title="Deductions" value={fmt(28500)} change="+8.2%" icon={TrendingDown} trend="up" />
        <StatCard title="Pending Returns" value="2" change="-50%" icon={FileText} trend="down" />
        <StatCard title="Tax Saved" value={fmt(85000)} change="+15.3%" icon={CheckCircle2} trend="up" />
      </div>
    </div>
  )
}

function ComingSoonTab({ label }: { label: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center justify-center rounded-2xl border border-white/10 bg-white/[0.02] backdrop-blur-xl p-20 text-center"
    >
      <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-500/20">
        <Zap className="h-8 w-8 text-blue-400" />
      </div>
      <h3 className="text-xl font-bold mb-2">{label}</h3>
      <p className="text-gray-400">This feature is coming soon.</p>
    </motion.div>
  )
}

function AppContent() {
  const [activeTab, setActiveTab] = useState<TabType>('dashboard')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [showNotifications, setShowNotifications] = useState(false)
  const [showBalance, setShowBalance] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const notificationRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (notificationRef.current && !notificationRef.current.contains(e.target as Node)) {
        setShowNotifications(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const unreadCount = mockNotifications.filter((n) => !n.read).length

  const navItems: { id: TabType; icon: React.ComponentType<{ className?: string }>; label: string }[] = [
    { id: 'dashboard', icon: BarChart3, label: 'Dashboard' },
    { id: 'mapper', icon: Map, label: 'Section Mapper' },
    { id: 'qa', icon: Zap, label: 'AI Assistant' },
    { id: 'profile', icon: Users, label: 'Profile Analysis' },
    { id: 'notice', icon: FileText, label: 'Notice Decoder' },
  ]

  const tabLabels: Record<TabType, string> = {
    dashboard: 'Dashboard',
    mapper: 'Section Mapper',
    qa: 'AI Assistant',
    profile: 'Profile Analysis',
    notice: 'Notice Decoder',
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 text-white">
      {/* Ambient background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-br from-blue-500/10 via-purple-500/10 to-transparent blur-3xl animate-pulse" />
        <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-tl from-purple-500/10 via-blue-500/10 to-transparent blur-3xl animate-pulse" />
      </div>

      {/* Sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.aside
            initial={{ x: -280 }}
            animate={{ x: 0 }}
            exit={{ x: -280 }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className="fixed left-0 top-0 z-40 h-screen w-64 border-r border-white/10 bg-gray-900/60 backdrop-blur-xl"
          >
            <div className="flex h-full flex-col p-6">
              {/* Logo */}
              <div className="mb-8 flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 text-lg font-bold">
                  ₹
                </div>
                <div>
                  <h1 className="text-xl font-bold">TaxGPT</h1>
                  <p className="text-xs text-gray-400">India Tax Assistant</p>
                </div>
              </div>

              {/* Nav */}
              <nav className="flex-1 space-y-1">
                {navItems.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={cn(
                      'flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all',
                      activeTab === item.id
                        ? 'bg-gradient-to-r from-blue-500/20 to-purple-500/20 text-white border border-white/10'
                        : 'text-gray-400 hover:bg-white/5 hover:text-white',
                    )}
                  >
                    <item.icon className="h-5 w-5" />
                    {item.label}
                  </button>
                ))}
              </nav>

              {/* AI CTA */}
              <div className="rounded-xl border border-white/10 bg-gradient-to-br from-blue-500/10 to-purple-500/10 p-4">
                <div className="mb-2 flex items-center gap-2">
                  <Zap className="h-5 w-5 text-yellow-400" />
                  <span className="text-sm font-semibold">AI Assistant</span>
                </div>
                <p className="mb-3 text-xs text-gray-400">Instant tax advice powered by Gemini</p>
                <button
                  onClick={() => setActiveTab('qa')}
                  className="w-full rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 px-4 py-2 text-sm font-medium transition-transform hover:scale-105"
                >
                  Ask TaxGPT
                </button>
              </div>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Main */}
      <div className={cn('transition-all duration-300', sidebarOpen ? 'ml-64' : 'ml-0')}>
        {/* Header */}
        <header className="sticky top-0 z-30 border-b border-white/10 bg-gray-900/60 backdrop-blur-xl">
          <div className="flex items-center justify-between px-6 py-4">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="rounded-lg p-2 hover:bg-white/5 transition-colors"
              >
                <Menu className="h-6 w-6" />
              </button>
              <div>
                <h2 className="text-xl font-bold">{tabLabels[activeTab]}</h2>
                <p className="text-xs text-gray-400">Income Tax Act 2025 · FY 2025-26</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {/* Search — only on relevant tabs */}
              {activeTab === 'dashboard' && (
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search…"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-52 rounded-xl border border-white/10 bg-white/5 py-2 pl-9 pr-4 text-sm backdrop-blur-sm placeholder:text-gray-500 focus:border-blue-500/50 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                  />
                </div>
              )}

              {/* Notifications */}
              <div className="relative" ref={notificationRef}>
                <button
                  onClick={() => setShowNotifications(!showNotifications)}
                  className="relative rounded-xl border border-white/10 bg-white/5 p-2 backdrop-blur-sm hover:bg-white/10 transition-colors"
                >
                  <Bell className="h-5 w-5" />
                  {unreadCount > 0 && (
                    <span className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-xs font-bold">
                      {unreadCount}
                    </span>
                  )}
                </button>

                <AnimatePresence>
                  {showNotifications && (
                    <motion.div
                      initial={{ opacity: 0, y: 10, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: 10, scale: 0.95 }}
                      className="absolute right-0 top-full mt-2 w-80 rounded-xl border border-white/10 bg-gray-900/95 backdrop-blur-xl shadow-2xl z-50"
                    >
                      <div className="p-4">
                        <h3 className="mb-4 font-semibold">Notifications</h3>
                        <div className="space-y-2">
                          {mockNotifications.map((n) => (
                            <div
                              key={n.id}
                              className={cn(
                                'rounded-lg border p-3 transition-colors',
                                n.read ? 'border-white/5 bg-white/[0.02]' : 'border-blue-500/20 bg-blue-500/5',
                              )}
                            >
                              <div className="mb-1 flex items-start justify-between gap-2">
                                <p className="text-sm font-medium">{n.title}</p>
                                {n.type === 'warning' && <AlertCircle className="h-4 w-4 shrink-0 text-yellow-400" />}
                                {n.type === 'success' && <CheckCircle2 className="h-4 w-4 shrink-0 text-green-400" />}
                                {n.type === 'info' && <Clock className="h-4 w-4 shrink-0 text-blue-400" />}
                              </div>
                              <p className="text-xs text-gray-400 mb-1">{n.message}</p>
                              <p className="text-xs text-gray-500">{n.time}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {/* Shield badge */}
              <div className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs text-gray-400 backdrop-blur-sm">
                <Shield className="h-4 w-4 text-blue-400" />
                Secured
              </div>
            </div>
          </div>
        </header>

        {/* Content */}
        <main className="p-6">
          <AnimatePresence mode="wait">
            {activeTab === 'dashboard' && (
              <motion.div key="dashboard" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <DashboardTab showBalance={showBalance} setShowBalance={setShowBalance} />
              </motion.div>
            )}
            {activeTab === 'mapper' && (
              <motion.div key="mapper" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <MapperTab />
              </motion.div>
            )}
            {activeTab === 'qa' && (
              <motion.div key="qa" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <ComingSoonTab label="AI Assistant" />
              </motion.div>
            )}
            {activeTab === 'profile' && (
              <motion.div key="profile" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <ComingSoonTab label="Profile Analysis" />
              </motion.div>
            )}
            {activeTab === 'notice' && (
              <motion.div key="notice" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <ComingSoonTab label="Notice Decoder" />
              </motion.div>
            )}
          </AnimatePresence>
        </main>
      </div>
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
