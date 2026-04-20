import { useState, useMemo, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ChevronDown, Search, ArrowLeftRight, BookOpen,
  Sparkles, AlertCircle, CheckCircle2, Info, X, Map
} from 'lucide-react'
import {
  useSectionsList,
  useCompareFromOld,
  useCompareFromNew,
  type SectionListItem,
} from '../hooks/useCompare'
import { useMappingAll } from '../hooks/useMapper'
import type { MappingEntry } from '../lib/types'

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

// ─── Inline mapper result card ────────────────────────────────────────────────

const CATEGORY_COLORS: Record<string, string> = {
  deductions: '#a78bfa',
  tds: '#60a5fa',
  returns: '#34d399',
  assessment: '#fb923c',
  exemptions: '#f472b6',
  general: '#94a3b8',
  default: '#94a3b8',
}

function MapperResultCard({ entry }: { entry: MappingEntry }) {
  if (entry.type === 'section') {
    const color = CATEGORY_COLORS[(entry.category || 'default').toLowerCase()] || CATEGORY_COLORS.default
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-2xl border p-6 space-y-5"
        style={{ background: 'rgba(255,255,255,0.025)', borderColor: `${color}30` }}
      >
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-full"
            style={{ background: `${color}20`, color }}>
            {entry.category || 'Section'}
          </span>
        </div>
        <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-4">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-widest text-amber-400/70 mb-1">1961 Act</p>
            <p className="text-4xl font-bold text-amber-400">{entry.old_section}</p>
            <p className="text-xs text-white/40 mt-1 leading-snug">{entry.title_old}</p>
          </div>
          <div className="flex flex-col items-center gap-1">
            <div className="h-px w-8 bg-white/10" />
            <ArrowLeftRight className="h-4 w-4 text-white/20" />
            <div className="h-px w-8 bg-white/10" />
          </div>
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-widest text-indigo-400/70 mb-1">2025 Act</p>
            <p className="text-4xl font-bold text-indigo-400">{entry.new_section}</p>
            <p className="text-xs text-white/40 mt-1 leading-snug">{entry.title_new}</p>
          </div>
        </div>
        {entry.change_summary && (
          <div className="pt-4 border-t border-white/8">
            <p className="text-[10px] font-semibold uppercase tracking-widest text-white/30 mb-2">What Changed</p>
            <p className="text-sm text-white/60 leading-relaxed">{entry.change_summary}</p>
          </div>
        )}
      </motion.div>
    )
  }

  if (entry.type === 'concept') {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-2xl border p-6 space-y-5"
        style={{ background: 'rgba(168,139,250,0.04)', borderColor: 'rgba(168,139,250,0.25)' }}
      >
        <span className="text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-full bg-violet-500/15 text-violet-400">
          Concept
        </span>
        <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-4">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-widest text-amber-400/70 mb-1">Old Term</p>
            <p className="text-2xl font-bold text-amber-400 leading-tight">{entry.old_concept}</p>
          </div>
          <ArrowLeftRight className="h-4 w-4 text-white/20" />
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-widest text-violet-400/70 mb-1">New Term (§{entry.new_section})</p>
            <p className="text-2xl font-bold text-violet-400 leading-tight">{entry.new_concept}</p>
          </div>
        </div>
        {entry.impact && (
          <div className="pt-4 border-t border-white/8">
            <p className="text-[10px] font-semibold uppercase tracking-widest text-white/30 mb-2">Impact</p>
            <p className="text-sm text-white/60 leading-relaxed">{entry.impact}</p>
          </div>
        )}
      </motion.div>
    )
  }

  // form
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-2xl border p-6 space-y-5"
      style={{ background: 'rgba(251,146,60,0.04)', borderColor: 'rgba(251,146,60,0.25)' }}
    >
      <span className="text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-full bg-orange-500/15 text-orange-400">
        Form
      </span>
      <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-4">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-widest text-amber-400/70 mb-1">Old Form</p>
          <p className="text-2xl font-bold text-amber-400 font-mono">{entry.old_form}</p>
        </div>
        <ArrowLeftRight className="h-4 w-4 text-white/20" />
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-widest text-orange-400/70 mb-1">New Form</p>
          <p className="text-2xl font-bold text-orange-400 font-mono">{entry.new_form}</p>
        </div>
      </div>
      {entry.purpose && (
        <div className="pt-4 border-t border-white/8">
          <p className="text-[10px] font-semibold uppercase tracking-widest text-white/30 mb-2">Purpose</p>
          <p className="text-sm text-white/60">{entry.purpose}</p>
        </div>
      )}
    </motion.div>
  )
}

// ─── Main component ───────────────────────────────────────────────────────────

export function CompareTab() {
  // ── Compare mode state ──
  const [direction, setDirection] = useState<'from-old' | 'from-new'>('from-old')
  const [oldSection, setOldSection] = useState<string | null>(null)
  const [newSection, setNewSection] = useState<string | null>(null)

  // ── Mapper mode state ──
  const [mapperMode, setMapperMode] = useState(false)
  const [mapperSearch, setMapperSearch] = useState('')
  const [selectedEntry, setSelectedEntry] = useState<MappingEntry | null>(null)
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const searchRef = useRef<HTMLDivElement>(null)
  const searchInputRef = useRef<HTMLInputElement>(null)

  const { data: allMappings, isLoading: mappingsLoading } = useMappingAll()

  const filteredEntries = useMemo(() => {
    if (!allMappings || !mapperSearch.trim()) return []
    const q = mapperSearch.trim().toLowerCase()
    return allMappings.filter(entry => {
      if (entry.type === 'section')
        return entry.old_section.toLowerCase().includes(q) || entry.title_old.toLowerCase().includes(q)
      if (entry.type === 'concept')
        return entry.old_concept.toLowerCase().includes(q) || entry.new_concept.toLowerCase().includes(q)
      if (entry.type === 'form')
        return entry.old_form.toLowerCase().includes(q) || entry.new_form.toLowerCase().includes(q)
      return false
    }).slice(0, 8)
  }, [allMappings, mapperSearch])

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) {
        setDropdownOpen(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  // ── Compare mode handlers ──
  const { data: sections1961, isLoading: loading1961 } = useSectionsList('1961')
  const { data: sections2025, isLoading: loading2025 } = useSectionsList('2025')

  const fromOld = useCompareFromOld(direction === 'from-old' ? oldSection : null)
  const fromNew = useCompareFromNew(direction === 'from-new' ? newSection : null)

  const result = direction === 'from-old' ? fromOld.data : fromNew.data
  const isLoading = direction === 'from-old' ? fromOld.isLoading : fromNew.isLoading

  const displayOldSection = result?.old_section || (direction === 'from-old' ? oldSection : null)
  const displayNewSection = result?.new_section || (direction === 'from-new' ? newSection : null)

  const handleSwap = () => setDirection(d => d === 'from-old' ? 'from-new' : 'from-old')
  const handleSelectOld = (sec: string) => { setOldSection(sec); setDirection('from-old') }
  const handleSelectNew = (sec: string) => { setNewSection(sec); setDirection('from-new') }

  const handleSelectEntry = (entry: MappingEntry) => {
    setSelectedEntry(entry)
    setMapperSearch(entry.type === 'section' ? entry.old_section : entry.type === 'concept' ? entry.old_concept : entry.old_form)
    setDropdownOpen(false)
  }

  const entryLabel = (entry: MappingEntry) => {
    if (entry.type === 'section') return `§${entry.old_section} — ${entry.title_old}`
    if (entry.type === 'concept') return `${entry.old_concept} → ${entry.new_concept}`
    return `${entry.old_form} → ${entry.new_form}`
  }

  const entryBadge = (entry: MappingEntry) => {
    if (entry.type === 'concept') return { label: 'Concept', color: '#a78bfa' }
    if (entry.type === 'form') return { label: 'Form', color: '#fb923c' }
    const color = CATEGORY_COLORS[(entry.category || 'default').toLowerCase()] || CATEGORY_COLORS.default
    return { label: entry.category || 'Section', color }
  }

  return (
    <div className="flex flex-col h-full gap-6 p-6 overflow-hidden">

      {/* Header */}
      <div className="flex items-center gap-4 shrink-0">
        <div>
          <h2 className="text-xl font-bold text-white">
            {mapperMode ? 'Section Mapper' : 'Parallel Reading Utility'}
          </h2>
          <p className="text-xs text-white/40 mt-0.5">
            {mapperMode
              ? 'Search sections, concepts, and forms — all from JSON, instant results'
              : 'Read provisions of the Income Tax Act, 1961 and 2025 side by side'}
          </p>
        </div>

        <div className="ml-auto flex items-center gap-3">
          {!mapperMode && (
            <div className="flex items-center gap-2 text-[11px] text-white/30">
              <Info className="h-3.5 w-3.5" />
              <span>Select a section from either Act to compare</span>
            </div>
          )}

          {/* Section Mapper checkbox */}
          <label className="flex items-center gap-2 cursor-pointer group select-none">
            <div
              onClick={() => {
                setMapperMode(m => !m)
                if (!mapperMode) setTimeout(() => searchInputRef.current?.focus(), 100)
              }}
              className={`relative flex h-5 w-5 shrink-0 items-center justify-center rounded border transition-all duration-200 ${
                mapperMode
                  ? 'border-indigo-500 bg-indigo-500'
                  : 'border-white/20 bg-white/5 group-hover:border-white/30'
              }`}
            >
              {mapperMode && (
                <motion.svg
                  initial={{ scale: 0 }} animate={{ scale: 1 }}
                  className="h-3 w-3 text-white" viewBox="0 0 12 12" fill="none"
                >
                  <path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                </motion.svg>
              )}
            </div>
            <span className="flex items-center gap-1.5 text-xs text-white/50 group-hover:text-white/70 transition-colors">
              <Map className="h-3.5 w-3.5" />
              Section Mapper
            </span>
          </label>
        </div>
      </div>

      {/* ── MAPPER MODE ── */}
      <AnimatePresence mode="wait">
        {mapperMode && (
          <motion.div
            key="mapper"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="flex flex-col gap-5 flex-1 overflow-y-auto"
          >
            {/* Search input + dropdown */}
            <div ref={searchRef} className="relative shrink-0">
              <p className="text-[11px] font-semibold uppercase tracking-widest text-indigo-400/70 mb-2">
                Search section, form, or concept
              </p>
              <div className="relative">
                <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-white/30 pointer-events-none" />
                <input
                  ref={searchInputRef}
                  type="text"
                  value={mapperSearch}
                  onChange={e => {
                    setMapperSearch(e.target.value)
                    setSelectedEntry(null)
                    setDropdownOpen(true)
                  }}
                  onFocus={() => mapperSearch && setDropdownOpen(true)}
                  placeholder={mappingsLoading ? 'Loading mappings…' : 'e.g. 80C, Form 16, Assessment Year'}
                  disabled={mappingsLoading}
                  className="w-full pl-10 pr-4 py-3 rounded-xl border bg-white/4 text-white placeholder-white/25 text-sm focus:outline-none transition-all disabled:opacity-50"
                  style={{ borderColor: dropdownOpen ? 'rgba(99,102,241,0.5)' : 'rgba(255,255,255,0.1)' }}
                />
                {mapperSearch && (
                  <button
                    onClick={() => { setMapperSearch(''); setSelectedEntry(null); setDropdownOpen(false); searchInputRef.current?.focus() }}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-white/30 hover:text-white/60"
                  >
                    <X className="h-4 w-4" />
                  </button>
                )}
              </div>

              {/* Dropdown list */}
              <AnimatePresence>
                {dropdownOpen && filteredEntries.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: -6, scale: 0.99 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -6, scale: 0.99 }}
                    transition={{ duration: 0.12 }}
                    className="absolute z-50 w-full mt-1.5 rounded-xl border overflow-hidden"
                    style={{
                      background: 'rgba(12,12,20,0.97)',
                      borderColor: 'rgba(99,102,241,0.25)',
                      boxShadow: '0 20px 60px rgba(0,0,0,0.6), 0 0 0 1px rgba(99,102,241,0.1)',
                      backdropFilter: 'blur(20px)',
                    }}
                  >
                    {filteredEntries.map((entry, i) => {
                      const badge = entryBadge(entry)
                      return (
                        <button
                          key={`${entry.type}-${entry.key}-${i}`}
                          onClick={() => handleSelectEntry(entry)}
                          className="w-full text-left px-4 py-2.5 flex items-start gap-3 transition-colors hover:bg-white/5 border-b border-white/4 last:border-0"
                        >
                          <span
                            className="shrink-0 mt-0.5 text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded"
                            style={{ background: `${badge.color}20`, color: badge.color }}
                          >
                            {badge.label}
                          </span>
                          <span className="text-xs text-white/70 leading-snug truncate">{entryLabel(entry)}</span>
                        </button>
                      )
                    })}
                    <div className="px-4 py-1.5 border-t border-white/6 text-[10px] text-white/20">
                      {filteredEntries.length} result{filteredEntries.length !== 1 ? 's' : ''} · JSON only, no API calls
                    </div>
                  </motion.div>
                )}
                {dropdownOpen && mapperSearch.trim() && filteredEntries.length === 0 && !mappingsLoading && (
                  <motion.div
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                    className="absolute z-50 w-full mt-1.5 rounded-xl border px-4 py-4 text-center text-sm text-white/30"
                    style={{ background: 'rgba(12,12,20,0.97)', borderColor: 'rgba(255,255,255,0.08)' }}
                  >
                    No match for "{mapperSearch}"
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Result card */}
            <AnimatePresence mode="wait">
              {selectedEntry ? (
                <MapperResultCard key={selectedEntry.key} entry={selectedEntry} />
              ) : !mapperSearch.trim() && allMappings ? (
                <motion.div
                  key="hint"
                  initial={{ opacity: 0 }} animate={{ opacity: 0.6 }} exit={{ opacity: 0 }}
                  className="flex flex-col items-center justify-center gap-3 py-16 text-center"
                >
                  <Map className="h-10 w-10 text-white/10" />
                  <p className="text-sm text-white/25">
                    {allMappings.length} mappings loaded · type above to search
                  </p>
                  <p className="text-xs text-white/15">Sections · Concepts · Forms</p>
                </motion.div>
              ) : null}
            </AnimatePresence>
          </motion.div>
        )}

        {/* ── COMPARE MODE (existing, untouched) ── */}
        {!mapperMode && (
          <motion.div
            key="compare"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="flex flex-col gap-6 flex-1 overflow-hidden"
          >
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

            {/* Change summary */}
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
                  initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }}
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
                  initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }}
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

            <p className="shrink-0 text-center text-[10px] text-white/20">
              Section text extracted from official PDFs. For authoritative reference, consult{' '}
              <span className="text-white/30">incometaxindia.gov.in</span>. Not legal advice.
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
