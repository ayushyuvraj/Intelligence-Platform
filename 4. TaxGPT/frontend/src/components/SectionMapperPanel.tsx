import { useState, useMemo, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search, ArrowLeftRight, BookOpen,
  Sparkles, X, ChevronLeft, Map,
} from 'lucide-react'
import { useMappingAll } from '../hooks/useMapper'
import { CategoryBento, groupEntries, type CatConfig } from './CategoryBento'
import type { MappingEntry } from '../lib/types'

// ─── Left panel: pill list for a selected category ────────────────────────────

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

function CategoryPills({
  cfg, entries, onSelect, onBack,
}: {
  cfg: CatConfig
  entries: MappingEntry[]
  onSelect: (e: MappingEntry) => void
  onBack: () => void
}) {
  return (
    <div className="h-full flex flex-col">
      <div className="shrink-0 flex items-center gap-2 mb-3">
        <button
          onClick={onBack}
          className="flex h-6 w-6 items-center justify-center rounded-lg text-white/30 hover:text-white/70 hover:bg-white/8 transition-all"
        >
          <ChevronLeft className="h-4 w-4" />
        </button>
        <cfg.Icon className="h-3.5 w-3.5" style={{ color: cfg.color }} />
        <span className="text-sm font-bold text-white/90 flex-1 truncate">{cfg.label}</span>
        <span
          className="text-[10px] font-bold px-1.5 py-0.5 rounded"
          style={{ background: `${cfg.color}18`, color: cfg.color }}
        >
          {entries.length}
        </span>
      </div>
      <div className="flex-1 overflow-y-auto space-y-1.5">
        {entries.map((entry) => (
          <motion.button
            key={`${entry.type}-${entry.key}`}
            onClick={() => onSelect(entry)}
            whileHover={{ x: 2 }}
            whileTap={{ scale: 0.98 }}
            className="w-full text-left rounded-xl border border-white/6 bg-white/[0.025] px-3 py-2.5 hover:border-white/14 hover:bg-white/[0.04] transition-all"
          >
            <p className="text-xs font-bold text-white/90 font-mono truncate" style={{ color: cfg.color }}>
              {pillLabel(entry)}
            </p>
            <p className="text-[10px] text-white/40 truncate mt-0.5 leading-snug">{pillSub(entry)}</p>
          </motion.button>
        ))}
      </div>
    </div>
  )
}

// ─── Left panel: entry detail result ─────────────────────────────────────────

function EntryDetail({ entry, onClose }: { entry: MappingEntry; onClose: () => void }) {
  const color =
    entry.type === 'section' ? '#a78bfa' :
    entry.type === 'concept' ? '#fde047' : '#67e8f9'

  return (
    <div className="h-full flex flex-col">
      <div className="shrink-0 flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <ArrowLeftRight className="h-3.5 w-3.5" style={{ color }} />
          <span className="text-xs font-semibold uppercase tracking-widest" style={{ color }}>
            {entry.type === 'section' ? 'Section' : entry.type === 'concept' ? 'Concept' : 'Form'}
          </span>
        </div>
        <button
          onClick={onClose}
          className="flex h-6 w-6 items-center justify-center rounded-lg text-white/30 hover:text-white/60 hover:bg-white/8 transition-all"
        >
          <X className="h-3.5 w-3.5" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3">
        {entry.type === 'section' && (
          <>
            <div className="rounded-xl border border-white/8 bg-white/[0.03] p-3">
              <p className="text-[10px] font-semibold uppercase tracking-widest text-white/35 mb-1">1961 Act</p>
              <p className="text-2xl font-black text-white/90">§{entry.old_section}</p>
              <p className="text-xs text-white/50 mt-1 leading-snug">{entry.title_old}</p>
            </div>
            <div className="flex justify-center">
              <ArrowLeftRight className="h-4 w-4 text-white/15 rotate-90" />
            </div>
            <div className="rounded-xl border p-3" style={{ borderColor: `${color}40`, background: `${color}0d` }}>
              <p className="text-[10px] font-semibold uppercase tracking-widest mb-1" style={{ color }}>2025 Act</p>
              <p className="text-2xl font-black" style={{ color }}>§{entry.new_section}</p>
              <p className="text-xs text-white/50 mt-1 leading-snug">{entry.title_new}</p>
            </div>
            {entry.change_summary && (
              <p className="text-xs text-white/45 leading-relaxed pt-1">{entry.change_summary}</p>
            )}
          </>
        )}

        {entry.type === 'concept' && (
          <>
            <div className="rounded-xl border border-white/8 bg-white/[0.03] p-3">
              <p className="text-[10px] font-semibold uppercase tracking-widest text-white/35 mb-1">Old Term</p>
              <p className="text-base font-bold text-white/90">{entry.old_concept}</p>
            </div>
            <div className="flex justify-center">
              <ArrowLeftRight className="h-4 w-4 text-white/15 rotate-90" />
            </div>
            <div className="rounded-xl border p-3" style={{ borderColor: `${color}40`, background: `${color}0d` }}>
              <p className="text-[10px] font-semibold uppercase tracking-widest mb-1" style={{ color }}>New Term · §{entry.new_section}</p>
              <p className="text-base font-bold" style={{ color }}>{entry.new_concept}</p>
            </div>
            {entry.impact && (
              <p className="text-xs text-white/45 leading-relaxed pt-1">{entry.impact}</p>
            )}
          </>
        )}

        {entry.type === 'form' && (
          <>
            <div className="rounded-xl border border-white/8 bg-white/[0.03] p-3">
              <p className="text-[10px] font-semibold uppercase tracking-widest text-white/35 mb-1">Old Form</p>
              <p className="text-xl font-black text-white/90 font-mono">{entry.old_form}</p>
            </div>
            <div className="flex justify-center">
              <ArrowLeftRight className="h-4 w-4 text-white/15 rotate-90" />
            </div>
            <div className="rounded-xl border p-3" style={{ borderColor: `${color}40`, background: `${color}0d` }}>
              <p className="text-[10px] font-semibold uppercase tracking-widest mb-1" style={{ color }}>New Form</p>
              <p className="text-xl font-black font-mono" style={{ color }}>{entry.new_form}</p>
            </div>
            {entry.purpose && (
              <p className="text-xs text-white/45 leading-relaxed pt-1">{entry.purpose}</p>
            )}
          </>
        )}
      </div>
    </div>
  )
}

// ─── Left panel: default placeholder ─────────────────────────────────────────

function BrowsePlaceholder() {
  return (
    <div className="h-full flex flex-col items-center justify-center gap-3 text-center px-4">
      <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/8 bg-white/[0.03]">
        <Map className="h-5 w-5 text-white/20" />
      </div>
      <div>
        <p className="text-sm font-semibold text-white/50">Browse or Search</p>
        <p className="text-xs text-white/25 mt-1 leading-snug">
          Click any category on the right, or type a section number, form, or concept above
        </p>
      </div>
    </div>
  )
}

// ─── Main panel ───────────────────────────────────────────────────────────────

type LeftMode =
  | { type: 'placeholder' }
  | { type: 'pills'; cfg: CatConfig; entries: MappingEntry[] }
  | { type: 'detail'; entry: MappingEntry }

export function SectionMapperPanel({ initialQuery }: { initialQuery?: string }) {
  const [search, setSearch] = useState('')
  const [activeCatId, setActiveCatId] = useState<string | null>(null)
  const [leftMode, setLeftMode] = useState<LeftMode>({ type: 'placeholder' })
  const lastAppliedQuery = useRef('')
  const { data: entries = [], isLoading } = useMappingAll()

  // Auto-apply deep-link query from dashboard
  useEffect(() => {
    if (!initialQuery || !entries.length || lastAppliedQuery.current === initialQuery) return
    lastAppliedQuery.current = initialQuery
    const q = initialQuery.toLowerCase()
    const match = entries.find(e => {
      if (e.type === 'section') return e.old_section.toLowerCase() === q || e.title_old.toLowerCase().includes(q)
      if (e.type === 'concept') return e.old_concept.toLowerCase().includes(q)
      return e.old_form.toLowerCase().includes(q)
    })
    if (match) {
      setLeftMode({ type: 'detail', entry: match })
    } else {
      setSearch(initialQuery)
    }
  }, [initialQuery, entries])

  const grouped = useMemo(() => groupEntries(entries), [entries])

  // Filtered entries for search mode
  const searchResults = useMemo(() => {
    const q = search.trim().toLowerCase()
    if (!q) return []
    return entries.filter(e => {
      if (e.type === 'section') return e.old_section.toLowerCase().includes(q) || e.title_old.toLowerCase().includes(q)
      if (e.type === 'concept') return e.old_concept.toLowerCase().includes(q) || e.new_concept.toLowerCase().includes(q)
      return e.old_form.toLowerCase().includes(q) || e.new_form.toLowerCase().includes(q)
    })
  }, [entries, search])

  const handleCategoryClick = (catId: string, catEntries: MappingEntry[], cfg: CatConfig) => {
    if (activeCatId === catId) {
      setActiveCatId(null)
      setLeftMode({ type: 'placeholder' })
    } else {
      setActiveCatId(catId)
      setLeftMode({ type: 'pills', cfg, entries: catEntries })
    }
  }

  const handleSelectEntry = (entry: MappingEntry) => {
    setLeftMode({ type: 'detail', entry })
  }

  const handleBack = () => {
    if (leftMode.type === 'detail') {
      if (activeCatId) {
        const cfg = { id: activeCatId } as CatConfig
        const catEntries = grouped[activeCatId] ?? []
        // find cfg from BENTO_CATS
        import('./CategoryBento').then(m => {
          const found = m.BENTO_CATS.find(c => c.id === activeCatId)
          if (found) setLeftMode({ type: 'pills', cfg: found, entries: catEntries })
          else setLeftMode({ type: 'placeholder' })
        })
      } else {
        setLeftMode({ type: 'placeholder' })
      }
    } else {
      setActiveCatId(null)
      setLeftMode({ type: 'placeholder' })
    }
  }

  return (
    <div className="h-full flex flex-col gap-4">
      {/* ── Top bar: title + search ── */}
      <div className="shrink-0 flex items-center gap-4">
        <div className="shrink-0">
          <h2 className="text-xl font-bold text-white">Section Mapper</h2>
          <p className="text-xs text-white/35 mt-0.5">1961 Act → 2025 Act · JSON only</p>
        </div>
        <div className="flex-1 relative">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-white/30 pointer-events-none" />
          <input
            type="text"
            placeholder="Search section, form, or concept…"
            value={search}
            onChange={e => {
              setSearch(e.target.value)
              if (e.target.value) {
                setActiveCatId(null)
                setLeftMode({ type: 'placeholder' })
              }
            }}
            className="w-full bg-white/[0.04] border border-white/8 rounded-xl pl-10 pr-10 py-2.5 text-sm text-white placeholder-white/25 focus:outline-none focus:border-white/20 focus:bg-white/[0.06] transition-all"
          />
          {search && (
            <button
              onClick={() => setSearch('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-white/30 hover:text-white/60 transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>

      {/* ── Two-panel body ── */}
      <div className="flex-1 flex gap-4 overflow-hidden">
        {/* Left panel */}
        <div className="w-72 shrink-0 rounded-2xl border border-white/6 bg-white/[0.03] p-4 overflow-hidden">
          <AnimatePresence mode="wait">
            {search.trim() ? (
              /* Search results in left panel */
              <motion.div
                key="search"
                initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -8 }}
                transition={{ duration: 0.15 }}
                className="h-full flex flex-col"
              >
                <p className="text-xs font-semibold text-white/40 mb-2 shrink-0">
                  {searchResults.length} result{searchResults.length !== 1 ? 's' : ''}
                </p>
                <div className="flex-1 overflow-y-auto space-y-1.5">
                  {searchResults.length === 0 ? (
                    <p className="text-xs text-white/25 text-center mt-8">No matches</p>
                  ) : searchResults.map(entry => {
                    const color =
                      entry.type === 'section' ? '#a78bfa' :
                      entry.type === 'concept' ? '#fde047' : '#67e8f9'
                    return (
                      <motion.button
                        key={`${entry.type}-${entry.key}`}
                        onClick={() => handleSelectEntry(entry)}
                        whileHover={{ x: 2 }}
                        className="w-full text-left rounded-xl border border-white/6 bg-white/[0.025] px-3 py-2.5 hover:bg-white/[0.05] transition-all"
                      >
                        <p className="text-xs font-bold font-mono truncate" style={{ color }}>
                          {entry.type === 'section' ? `§${entry.old_section}` : entry.type === 'concept' ? entry.old_concept : entry.old_form}
                        </p>
                        <p className="text-[10px] text-white/40 truncate mt-0.5">
                          {entry.type === 'section' ? entry.title_old : entry.type === 'concept' ? `→ ${entry.new_concept}` : `→ ${entry.new_form}`}
                        </p>
                      </motion.button>
                    )
                  })}
                </div>
              </motion.div>
            ) : leftMode.type === 'placeholder' ? (
              <motion.div key="placeholder" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.15 }} className="h-full">
                <BrowsePlaceholder />
              </motion.div>
            ) : leftMode.type === 'pills' ? (
              <motion.div key={`pills-${leftMode.cfg.id}`} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -8 }} transition={{ duration: 0.15 }} className="h-full">
                <CategoryPills
                  cfg={leftMode.cfg}
                  entries={leftMode.entries}
                  onSelect={handleSelectEntry}
                  onBack={handleBack}
                />
              </motion.div>
            ) : (
              <motion.div key="detail" initial={{ opacity: 0, x: 8 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 8 }} transition={{ duration: 0.15 }} className="h-full">
                <EntryDetail entry={leftMode.entry} onClose={handleBack} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Right panel: bento grid */}
        <div className="flex-1 overflow-hidden relative">
          {isLoading ? (
            <div className="flex items-center justify-center h-full gap-3">
              <Sparkles className="h-5 w-5 text-indigo-400 animate-pulse" />
              <p className="text-sm text-white/40">Loading mappings…</p>
            </div>
          ) : (
            <div className="absolute inset-0">
              <CategoryBento
                entries={entries}
                onCategoryClick={handleCategoryClick}
                activeCatId={activeCatId}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
