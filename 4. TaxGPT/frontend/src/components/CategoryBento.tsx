import { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Wallet, Briefcase, TrendingUp, Globe, Scale, Lightbulb,
  Home, ShieldCheck, Layers, Settings2, UserCheck, Receipt,
  Gavel, LayoutGrid, Banknote, Percent, Calendar, FileStack,
  ClipboardCheck, AlertTriangle, BookOpen, FileText, X,
} from 'lucide-react'
import type { MappingEntry } from '../lib/types'

type IconType = React.ComponentType<{ className?: string; style?: React.CSSProperties }>

interface CatConfig {
  id: string
  label: string
  color: string
  Icon: IconType
  desc: string
  span?: 2
}

const CATS: CatConfig[] = [
  { id: 'deductions',    label: 'Deductions',    color: '#a78bfa', Icon: Wallet,        desc: '§80C, §80D and all deduction chapters',        span: 2 },
  { id: 'capital_gains', label: 'Capital Gains', color: '#34d399', Icon: TrendingUp,    desc: 'LTCG, STCG, STT and all asset transfers',      span: 2 },
  { id: 'business',      label: 'Business',      color: '#60a5fa', Icon: Briefcase,     desc: 'Business income and presumptive tax' },
  { id: 'penalties',     label: 'Penalties',     color: '#f87171', Icon: AlertTriangle, desc: 'Late filing, concealment, defaults' },
  { id: 'assessment',    label: 'Assessment',    color: '#fb923c', Icon: ClipboardCheck,desc: 'Scrutiny, reopening, best judgment' },
  { id: 'international', label: 'International', color: '#22d3ee', Icon: Globe,         desc: 'DTAA, transfer pricing, POEM' },
  { id: 'definitions',   label: 'Definitions',   color: '#94a3b8', Icon: BookOpen,      desc: 'Key terms and interpretation clauses' },
  { id: 'appeals',       label: 'Appeals',       color: '#fbbf24', Icon: Scale,         desc: 'CIT(A), ITAT, High Court, Supreme Court' },
  { id: 'income',        label: 'Income',        color: '#4ade80', Icon: Banknote,      desc: 'Heads of income and chargeability' },
  { id: 'returns',       label: 'Returns',       color: '#6366f1', Icon: FileText,      desc: 'ITR filing deadlines and requirements' },
  { id: 'house_property',label: 'House Property',color: '#2dd4bf', Icon: Home,          desc: 'HRA, home loan interest, let-out' },
  { id: 'tds',           label: 'TDS',           color: '#38bdf8', Icon: Layers,        desc: 'Tax deducted at source — §393 consolidated' },
  { id: 'salary',        label: 'Salary',        color: '#fb7185', Icon: UserCheck,     desc: 'Perquisites, allowances, standard deduction' },
  { id: 'advance_tax',   label: 'Advance Tax',   color: '#818cf8', Icon: Calendar,      desc: 'Quarterly advance tax instalments' },
  { id: 'interest',      label: 'Interest',      color: '#f472b6', Icon: Percent,       desc: 'Interest on delayed payments and refunds' },
  { id: 'exemptions',    label: 'Exemptions',    color: '#a3e635', Icon: ShieldCheck,   desc: 'Agricultural, charitable, HUF exemptions' },
  { id: 'procedures',    label: 'Procedures',    color: '#64748b', Icon: Settings2,     desc: 'Search, seizure and rectification' },
  { id: 'tcs',           label: 'TCS',           color: '#fdba74', Icon: Receipt,       desc: 'Tax collected at source by sellers' },
  { id: 'prosecution',   label: 'Prosecution',   color: '#ef4444', Icon: Gavel,         desc: 'Criminal offences and prosecution' },
  { id: 'general',       label: 'General',       color: '#6b7280', Icon: LayoutGrid,    desc: 'Administrative and miscellaneous provisions' },
  { id: '_concepts',     label: 'Concepts',      color: '#fde047', Icon: Lightbulb,     desc: '16 key terminology changes in the 2025 Act', span: 2 },
  { id: '_forms',        label: 'Forms',         color: '#67e8f9', Icon: FileStack,     desc: '17 tax form numbers changed — ITR, TDS, PAN', span: 2 },
]

// ─── Helpers ──────────────────────────────────────────────────────────────────

function pillLabel(e: MappingEntry): string {
  if (e.type === 'section') return `§${e.old_section} → §${e.new_section}`
  if (e.type === 'concept') return e.old_concept
  return e.old_form
}

function pillSub(e: MappingEntry): string {
  if (e.type === 'section') return e.title_old
  if (e.type === 'concept') return `→ ${e.new_concept}`
  return `→ ${e.new_form}`
}

// ─── Main component ───────────────────────────────────────────────────────────

interface CategoryBentoProps {
  entries: MappingEntry[]
  onSelectEntry: (entry: MappingEntry) => void
}

export function CategoryBento({ entries, onSelectEntry }: CategoryBentoProps) {
  const [activeCat, setActiveCat] = useState<string | null>(null)
  const [showAll, setShowAll] = useState(false)
  const PILL_LIMIT = 30

  const grouped = useMemo(() => {
    const map: Record<string, MappingEntry[]> = {}
    for (const entry of entries) {
      const key =
        entry.type === 'concept' ? '_concepts' :
        entry.type === 'form'    ? '_forms' :
        (entry as Extract<MappingEntry, { type: 'section' }>).category || 'general'
      if (!map[key]) map[key] = []
      map[key].push(entry)
    }
    return map
  }, [entries])

  const handleCatClick = (id: string) => {
    setActiveCat(prev => prev === id ? null : id)
    setShowAll(false)
  }

  const activeEntries  = activeCat ? (grouped[activeCat] ?? []) : []
  const displayEntries = showAll ? activeEntries : activeEntries.slice(0, PILL_LIMIT)
  const activeCfg      = CATS.find(c => c.id === activeCat)

  return (
    <div className="flex flex-col gap-3">

      {/* ── Bento grid ── */}
      <div className="grid grid-cols-4 gap-2.5">
        {CATS.map(cfg => {
          const count = grouped[cfg.id]?.length ?? 0
          if (count === 0) return null

          const isActive = activeCat === cfg.id
          const colSpan  = cfg.span === 2 ? 'col-span-2' : 'col-span-1'

          return (
            <motion.button
              key={cfg.id}
              onClick={() => handleCatClick(cfg.id)}
              className={`${colSpan} relative overflow-hidden text-left rounded-2xl border p-4 group transition-shadow duration-300`}
              whileHover={{ y: -2, transition: { duration: 0.15 } }}
              whileTap={{ scale: 0.97 }}
              style={{
                background: isActive
                  ? `linear-gradient(135deg, ${cfg.color}18 0%, ${cfg.color}08 100%)`
                  : 'rgba(255,255,255,0.025)',
                borderColor: isActive
                  ? `${cfg.color}55`
                  : 'rgba(255,255,255,0.07)',
                boxShadow: isActive
                  ? `0 0 28px ${cfg.color}18, inset 0 1px 0 ${cfg.color}18`
                  : 'none',
              }}
            >
              {/* Hover radial glow */}
              <div
                className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none rounded-2xl"
                style={{ background: `radial-gradient(ellipse at 25% 40%, ${cfg.color}12 0%, transparent 65%)` }}
              />

              {/* Active bottom bar */}
              <motion.div
                className="absolute bottom-0 left-3 right-3 h-[2px] rounded-full"
                style={{ background: `linear-gradient(to right, ${cfg.color}, transparent)` }}
                initial={{ scaleX: 0, opacity: 0 }}
                animate={{ scaleX: isActive ? 1 : 0, opacity: isActive ? 1 : 0 }}
                transition={{ duration: 0.25 }}
              />

              <div className="relative flex flex-col gap-2.5">
                {/* Icon + count */}
                <div className="flex items-start justify-between gap-2">
                  <div
                    className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl"
                    style={{ background: `${cfg.color}1a` }}
                  >
                    <cfg.Icon className="h-4 w-4" style={{ color: cfg.color }} />
                  </div>
                  <span
                    className="text-[10px] font-extrabold tabular-nums px-1.5 py-0.5 rounded-md leading-none mt-1"
                    style={{ background: `${cfg.color}18`, color: cfg.color }}
                  >
                    {count}
                  </span>
                </div>

                {/* Text */}
                <div>
                  <p className="text-[13px] font-semibold text-white/90 leading-tight">{cfg.label}</p>
                  <p className="text-[10.5px] text-white/30 mt-0.5 leading-snug line-clamp-2">{cfg.desc}</p>
                </div>
              </div>
            </motion.button>
          )
        })}
      </div>

      {/* ── Expanded pill panel ── */}
      <AnimatePresence>
        {activeCat && activeCfg && (
          <motion.div
            key={activeCat}
            initial={{ opacity: 0, height: 0, marginTop: 0 }}
            animate={{ opacity: 1, height: 'auto', marginTop: 4 }}
            exit={{ opacity: 0, height: 0, marginTop: 0 }}
            transition={{ duration: 0.22, ease: [0.4, 0, 0.2, 1] }}
            className="overflow-hidden"
          >
            <div
              className="rounded-2xl border p-4"
              style={{
                background: `linear-gradient(135deg, ${activeCfg.color}0a 0%, rgba(255,255,255,0.01) 100%)`,
                borderColor: `${activeCfg.color}28`,
                boxShadow: `0 4px 32px ${activeCfg.color}08`,
              }}
            >
              {/* Panel header */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <activeCfg.Icon className="h-3.5 w-3.5" style={{ color: activeCfg.color }} />
                  <span className="text-sm font-bold text-white">{activeCfg.label}</span>
                  <span
                    className="text-[9px] font-extrabold uppercase tracking-wider px-1.5 py-0.5 rounded"
                    style={{ background: `${activeCfg.color}18`, color: activeCfg.color }}
                  >
                    {activeEntries.length} entries
                  </span>
                </div>
                <button
                  onClick={() => { setActiveCat(null); setShowAll(false) }}
                  className="flex h-6 w-6 items-center justify-center rounded-lg text-white/30 hover:text-white/70 hover:bg-white/8 transition-all"
                >
                  <X className="h-3.5 w-3.5" />
                </button>
              </div>

              {/* Pills */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {displayEntries.map((entry, i) => (
                  <motion.button
                    key={`${entry.type}-${entry.key}`}
                    initial={{ opacity: 0, scale: 0.94 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: Math.min(i * 0.012, 0.25), duration: 0.14 }}
                    onClick={() => { onSelectEntry(entry); setActiveCat(null) }}
                    className="text-left rounded-xl border px-3 py-2.5 group/pill transition-all duration-150"
                    style={{
                      background: 'rgba(255,255,255,0.03)',
                      borderColor: `${activeCfg.color}1a`,
                    }}
                    whileHover={{
                      backgroundColor: `${activeCfg.color}14`,
                      borderColor: `${activeCfg.color}45`,
                      y: -1,
                    }}
                  >
                    <p className="text-[11px] font-bold text-white/90 truncate font-mono">
                      {pillLabel(entry)}
                    </p>
                    <p className="text-[10px] text-white/35 truncate mt-0.5 group-hover/pill:text-white/55 transition-colors leading-snug">
                      {pillSub(entry)}
                    </p>
                  </motion.button>
                ))}
              </div>

              {/* Show more */}
              {!showAll && activeEntries.length > PILL_LIMIT && (
                <motion.button
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  onClick={() => setShowAll(true)}
                  className="mt-3 w-full text-center text-xs py-2.5 rounded-xl border border-white/8 text-white/35 hover:text-white/60 hover:bg-white/4 transition-all"
                >
                  Show {activeEntries.length - PILL_LIMIT} more ↓
                </motion.button>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
