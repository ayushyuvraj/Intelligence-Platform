import { useState, useMemo, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ChevronDown, Search, ArrowLeftRight, BookOpen,
  Sparkles, AlertCircle, CheckCircle2, Info, X
} from 'lucide-react'
import {
  useSectionsList,
  useCompareFromOld,
  useCompareFromNew,
  type SectionListItem,
} from '../hooks/useCompare'

// ─── Searchable dropdown ──────────────────────────────────────────────────────

interface DropdownProps {
  items: SectionListItem[]
  value: string | null
  onChange: (section: string) => void
  placeholder: string
  accentColor: string
  loading?: boolean
  label: string
}

function SectionDropdown({
  items, value, onChange, placeholder, accentColor, loading, label
}: DropdownProps) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const ref = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const filtered = useMemo(() => {
    if (!query) return items
    const q = query.toLowerCase()
    return items.filter(
      (i) =>
        i.section.toLowerCase().includes(q) ||
        i.label.toLowerCase().includes(q)
    )
  }, [items, query])

  const selected = items.find((i) => i.section === value)

  // Close on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false)
        setQuery('')
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  return (
    <div ref={ref} className="relative w-full">
      <p className="text-[11px] font-semibold uppercase tracking-widest mb-2" style={{ color: accentColor }}>
        {label}
      </p>
      <button
        onClick={() => { setOpen(!open); setTimeout(() => inputRef.current?.focus(), 50) }}
        className="w-full flex items-center justify-between gap-3 px-4 py-3 rounded-xl border text-sm font-medium transition-all duration-200"
        style={{
          background: 'rgba(255,255,255,0.04)',
          borderColor: open ? accentColor : 'rgba(255,255,255,0.1)',
          color: selected ? 'white' : 'rgba(255,255,255,0.4)',
          boxShadow: open ? `0 0 0 1px ${accentColor}40, 0 8px 32px rgba(0,0,0,0.3)` : 'none',
        }}
      >
        <span className="truncate text-left">
          {loading ? 'Loading sections...' : (selected?.label || placeholder)}
        </span>
        <motion.div animate={{ rotate: open ? 180 : 0 }} transition={{ duration: 0.2 }}>
          <ChevronDown className="h-4 w-4 shrink-0 opacity-60" />
        </motion.div>
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -8, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.98 }}
            transition={{ duration: 0.15 }}
            className="absolute z-50 w-full mt-2 rounded-xl border overflow-hidden"
            style={{
              background: 'rgba(15,15,25,0.97)',
              borderColor: 'rgba(255,255,255,0.12)',
              boxShadow: `0 20px 60px rgba(0,0,0,0.6), 0 0 0 1px ${accentColor}30`,
              backdropFilter: 'blur(20px)',
            }}
          >
            {/* Search input */}
            <div className="flex items-center gap-2 px-3 py-2 border-b border-white/8">
              <Search className="h-3.5 w-3.5 opacity-40 shrink-0" />
              <input
                ref={inputRef}
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search section number or title..."
                className="flex-1 bg-transparent text-sm text-white placeholder-white/30 outline-none"
              />
              {query && (
                <button onClick={() => setQuery('')} className="opacity-40 hover:opacity-70">
                  <X className="h-3 w-3" />
                </button>
              )}
            </div>

            {/* List */}
            <div className="max-h-64 overflow-y-auto">
              {filtered.length === 0 ? (
                <p className="text-center text-xs text-white/30 py-6">No sections found</p>
              ) : (
                filtered.map((item) => (
                  <button
                    key={item.section}
                    onClick={() => { onChange(item.section); setOpen(false); setQuery('') }}
                    className="w-full text-left px-4 py-2.5 text-sm transition-colors hover:bg-white/6 flex items-start gap-3"
                    style={{
                      background: value === item.section ? `${accentColor}18` : undefined,
                      color: value === item.section ? 'white' : 'rgba(255,255,255,0.7)',
                    }}
                  >
                    <span
                      className="shrink-0 text-xs font-bold mt-0.5 px-1.5 py-0.5 rounded"
                      style={{ background: `${accentColor}25`, color: accentColor }}
                    >
                      {item.section}
                    </span>
                    <span className="leading-snug text-xs">
                      {item.label.replace(`${item.section} — `, '').replace(item.section, '') || `Section ${item.section}`}
                    </span>
                  </button>
                ))
              )}
            </div>

            <div className="px-3 py-2 border-t border-white/6 text-[10px] text-white/20 text-center">
              {filtered.length} of {items.length} sections
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// ─── Section text panel ───────────────────────────────────────────────────────

interface TextPanelProps {
  act: '1961' | '2025'
  section: string | null
  text: string | null
  found: boolean
  loading: boolean
  accentColor: string
  title?: string
}

function TextPanel({ act, section, text, found, loading, accentColor, title }: TextPanelProps) {
  const isEmpty = !section

  return (
    <div
      className="flex flex-col h-full rounded-2xl overflow-hidden border"
      style={{
        background: 'rgba(255,255,255,0.02)',
        borderColor: section ? `${accentColor}30` : 'rgba(255,255,255,0.06)',
        boxShadow: section ? `0 0 40px ${accentColor}08, inset 0 1px 0 rgba(255,255,255,0.04)` : 'none',
      }}
    >
      {/* Panel header */}
      <div
        className="px-5 py-4 border-b flex items-center gap-3"
        style={{
          borderColor: 'rgba(255,255,255,0.06)',
          background: `linear-gradient(135deg, ${accentColor}12 0%, transparent 100%)`,
        }}
      >
        <div
          className="flex h-8 w-8 items-center justify-center rounded-lg shrink-0"
          style={{ background: `${accentColor}20` }}
        >
          <BookOpen className="h-4 w-4" style={{ color: accentColor }} />
        </div>
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-widest" style={{ color: accentColor }}>
            Income Tax Act, {act}
          </p>
          {section && (
            <p className="text-sm font-bold text-white truncate mt-0.5">
              Section {section}
              {title && <span className="font-normal text-white/50 ml-1">— {title}</span>}
            </p>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-5">
        <AnimatePresence mode="wait">
          {isEmpty ? (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex flex-col items-center justify-center h-full gap-4 py-16"
            >
              <div
                className="h-16 w-16 rounded-2xl flex items-center justify-center"
                style={{ background: `${accentColor}10` }}
              >
                <BookOpen className="h-7 w-7" style={{ color: `${accentColor}60` }} />
              </div>
              <p className="text-sm text-white/30 text-center max-w-[200px]">
                Select a section from the dropdown above to view its provisions
              </p>
            </motion.div>
          ) : loading ? (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex flex-col items-center justify-center h-full gap-4 py-16"
            >
              <motion.div
                className="h-8 w-8 rounded-full border-2"
                style={{ borderColor: `${accentColor}40`, borderTopColor: accentColor }}
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
              />
              <p className="text-xs text-white/30">Extracting section text...</p>
            </motion.div>
          ) : !found ? (
            <motion.div
              key="notfound"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col items-center justify-center gap-3 py-12"
            >
              <AlertCircle className="h-8 w-8" style={{ color: `${accentColor}60` }} />
              <p className="text-sm text-white/40 text-center">
                Section {section} text not available in this dataset
              </p>
            </motion.div>
          ) : (
            <motion.div
              key={`text-${section}`}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <div
                className="text-sm leading-relaxed whitespace-pre-wrap font-mono text-white/80 selection:bg-indigo-500/30"
                style={{ fontSize: '13px', lineHeight: '1.8' }}
              >
                {text}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

// ─── Change summary badge ─────────────────────────────────────────────────────

function ChangeBadge({ mapping }: { mapping: NonNullable<{ change_summary?: string; category?: string; title_new?: string }> }) {
  const categoryColors: Record<string, string> = {
    deductions: '#a78bfa',
    tds: '#60a5fa',
    returns: '#34d399',
    assessment: '#fb923c',
    exemptions: '#f472b6',
    default: '#94a3b8',
  }
  const cat = (mapping.category || 'default').toLowerCase()
  const color = categoryColors[cat] || categoryColors.default

  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      className="mx-auto max-w-2xl rounded-2xl border p-4 flex flex-col gap-2"
      style={{
        background: 'rgba(255,255,255,0.02)',
        borderColor: `${color}30`,
      }}
    >
      <div className="flex items-center gap-2">
        <Sparkles className="h-3.5 w-3.5" style={{ color }} />
        <span className="text-[10px] font-bold uppercase tracking-widest" style={{ color }}>
          {mapping.category || 'Change Summary'}
        </span>
      </div>
      <p className="text-sm text-white/70 leading-relaxed">{mapping.change_summary}</p>
    </motion.div>
  )
}

// ─── Main component ───────────────────────────────────────────────────────────

export function CompareTab() {
  const [direction, setDirection] = useState<'from-old' | 'from-new'>('from-old')
  const [oldSection, setOldSection] = useState<string | null>(null)
  const [newSection, setNewSection] = useState<string | null>(null)

  const { data: sections1961, isLoading: loading1961 } = useSectionsList('1961')
  const { data: sections2025, isLoading: loading2025 } = useSectionsList('2025')

  const fromOld = useCompareFromOld(direction === 'from-old' ? oldSection : null)
  const fromNew = useCompareFromNew(direction === 'from-new' ? newSection : null)

  const result = direction === 'from-old' ? fromOld.data : fromNew.data
  const isLoading = direction === 'from-old' ? fromOld.isLoading : fromNew.isLoading

  // When user picks from old side, auto-select the mapped new section for display
  const displayOldSection = result?.old_section || (direction === 'from-old' ? oldSection : null)
  const displayNewSection = result?.new_section || (direction === 'from-new' ? newSection : null)

  const handleSwap = () => {
    setDirection(d => d === 'from-old' ? 'from-new' : 'from-old')
  }

  const handleSelectOld = (sec: string) => {
    setOldSection(sec)
    setDirection('from-old')
  }

  const handleSelectNew = (sec: string) => {
    setNewSection(sec)
    setDirection('from-new')
  }

  return (
    <div className="flex flex-col h-full gap-6 p-6 overflow-hidden">

      {/* Header */}
      <div className="flex items-center gap-4 shrink-0">
        <div>
          <h2 className="text-xl font-bold text-white">Parallel Reading Utility</h2>
          <p className="text-xs text-white/40 mt-0.5">
            Read provisions of the Income Tax Act, 1961 and 2025 side by side
          </p>
        </div>
        <div className="ml-auto flex items-center gap-2 text-[11px] text-white/30">
          <Info className="h-3.5 w-3.5" />
          <span>Select a section from either Act to compare</span>
        </div>
      </div>

      {/* Dropdowns row */}
      <div className="shrink-0 flex items-end gap-4">
        <div className="flex-1">
          <SectionDropdown
            label="Income Tax Act, 1961 (Old Law)"
            items={sections1961?.sections || []}
            value={displayOldSection}
            onChange={handleSelectOld}
            placeholder="Select section from 1961 Act..."
            accentColor="#f59e0b"
            loading={loading1961}
          />
        </div>

        {/* Swap button */}
        <button
          onClick={handleSwap}
          className="shrink-0 mb-0.5 flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 transition-all hover:border-white/20 hover:bg-white/6"
          title="Swap direction"
        >
          <ArrowLeftRight className="h-4 w-4 text-white/40" />
        </button>

        <div className="flex-1">
          <SectionDropdown
            label="Income Tax Act, 2025 (New Law)"
            items={sections2025?.sections || []}
            value={displayNewSection}
            onChange={handleSelectNew}
            placeholder="Select section from 2025 Act..."
            accentColor="#6366f1"
            loading={loading2025}
          />
        </div>
      </div>

      {/* Change summary (when mapping available) */}
      <AnimatePresence>
        {result?.mapping?.change_summary && (
          <div className="shrink-0">
            <ChangeBadge mapping={result.mapping} />
          </div>
        )}
      </AnimatePresence>

      {/* Mapping auto-match notice */}
      <AnimatePresence>
        {result && result.new_section && direction === 'from-old' && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="shrink-0 flex items-center gap-2 px-4 py-2.5 rounded-xl border border-green-500/20 bg-green-500/5"
          >
            <CheckCircle2 className="h-3.5 w-3.5 text-green-400 shrink-0" />
            <p className="text-xs text-green-400/80">
              Section <strong className="text-green-300">{result.old_section}</strong> of the 1961 Act corresponds to
              Section <strong className="text-green-300">{result.new_section}</strong> of the Income Tax Act, 2025
            </p>
          </motion.div>
        )}
        {result && result.old_section && direction === 'from-new' && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="shrink-0 flex items-center gap-2 px-4 py-2.5 rounded-xl border border-indigo-500/20 bg-indigo-500/5"
          >
            <CheckCircle2 className="h-3.5 w-3.5 text-indigo-400 shrink-0" />
            <p className="text-xs text-indigo-400/80">
              Section <strong className="text-indigo-300">{result.new_section}</strong> of the 2025 Act corresponds to
              Section <strong className="text-indigo-300">{result.old_section}</strong> of the Income Tax Act, 1961
            </p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Side-by-side text panels */}
      <div className="flex-1 grid grid-cols-2 gap-4 min-h-0">
        <TextPanel
          act="1961"
          section={displayOldSection}
          text={result?.old_text || null}
          found={result?.old_found || false}
          loading={isLoading}
          accentColor="#f59e0b"
          title={result?.mapping?.title_old}
        />

        {/* Divider */}
        <div
          className="absolute left-1/2 top-0 bottom-0 w-px pointer-events-none"
          style={{
            background: 'linear-gradient(to bottom, transparent, rgba(99,102,241,0.3) 20%, rgba(245,158,11,0.3) 80%, transparent)',
          }}
        />

        <TextPanel
          act="2025"
          section={displayNewSection}
          text={result?.new_text || null}
          found={result?.new_found || false}
          loading={isLoading}
          accentColor="#6366f1"
          title={result?.mapping?.title_new}
        />
      </div>

      {/* Disclaimer */}
      <p className="shrink-0 text-center text-[10px] text-white/20">
        Section text extracted from official PDFs. For authoritative reference, consult{' '}
        <span className="text-white/30">incometaxindia.gov.in</span>. Not legal advice.
      </p>
    </div>
  )
}
