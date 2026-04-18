import { useState } from 'react'
import { useMapperLookup, useMapperStats } from '../hooks/useMapper'
import type { MapperResponse } from '../lib/types'

export function MapperTab() {
  const [section, setSection] = useState('')
  const mapperMutation = useMapperLookup()
  const statsQuery = useMapperStats()

  const handleLookup = async () => {
    if (!section.trim()) return
    await mapperMutation.mutateAsync(section)
  }

  const result = mapperMutation.data as MapperResponse | undefined

  return (
    <div className="space-y-12">
      {/* Search */}
      <div>
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">Search by section, form, or concept</label>
        </div>
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <input
              type="text"
              placeholder="e.g., 80C, 192, Form 16"
              value={section}
              onChange={(e) => setSection(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleLookup()}
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 transition-all duration-200 text-white placeholder-gray-600"
            />
          </div>
          <button
            onClick={handleLookup}
            disabled={mapperMutation.isPending || !section.trim()}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white font-medium rounded-lg transition-colors duration-200 disabled:cursor-not-allowed"
          >
            {mapperMutation.isPending ? 'Searching...' : 'Search'}
          </button>
        </div>
      </div>

      {/* Stats */}
      {statsQuery.data && (
        <div className="grid grid-cols-3 gap-6">
          {[
            { label: 'Old → New', value: statsQuery.data.total_old_to_new },
            { label: 'Concepts', value: statsQuery.data.total_concepts },
            { label: 'Forms', value: statsQuery.data.total_forms },
          ].map((stat) => (
            <div key={stat.label} className="bg-white/5 border border-white/10 rounded-lg p-6 hover:bg-white/8 transition-colors duration-300">
              <p className="text-gray-400 text-sm mb-2">{stat.label}</p>
              <p className="text-3xl font-bold">{stat.value}</p>
            </div>
          ))}
        </div>
      )}

      {/* Results */}
      {mapperMutation.isError && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-6 text-red-300 text-sm">
          Error: {mapperMutation.error instanceof Error ? mapperMutation.error.message : 'Search failed'}
        </div>
      )}

      {result && result.found && (
        <div className="space-y-6">
          {result.type === 'section' && (
            <div className="bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border border-blue-500/20 rounded-2xl p-8">
              <h3 className="text-lg font-semibold mb-8 text-white">Section Mapping</h3>

              <div className="space-y-6">
                {/* Old Section */}
                <div>
                  <p className="text-xs font-medium text-gray-400 mb-2">INCOME TAX ACT 1961</p>
                  <div className="flex items-baseline gap-4">
                    <p className="text-5xl font-bold text-blue-400">{result.old_section}</p>
                    <p className="text-gray-400 text-sm flex-1">{result.title_old}</p>
                  </div>
                </div>

                {/* Arrow */}
                <div className="flex justify-center py-4">
                  <div className="text-2xl text-gray-600">↓</div>
                </div>

                {/* New Section */}
                <div>
                  <p className="text-xs font-medium text-gray-400 mb-2">INCOME TAX ACT 2025</p>
                  <div className="flex items-baseline gap-4">
                    <p className="text-5xl font-bold text-green-400">{result.new_section}</p>
                    <p className="text-gray-400 text-sm flex-1">{result.title_new}</p>
                  </div>
                </div>

                {/* Change Summary */}
                <div className="mt-8 pt-8 border-t border-white/10">
                  <p className="text-xs font-medium text-gray-400 mb-3">WHAT CHANGED</p>
                  <p className="text-gray-300">{result.change_summary}</p>
                  <div className="mt-4">
                    <span className="inline-block px-3 py-1 bg-white/10 rounded-full text-xs text-gray-300 capitalize">
                      {result.category}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {result.type === 'concept' && (
            <div className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/20 rounded-2xl p-8">
              <h3 className="text-lg font-semibold mb-8 text-white">Concept Mapping</h3>
              <div className="space-y-6">
                <div>
                  <p className="text-xs font-medium text-gray-400 mb-2">OLD CONCEPT</p>
                  <p className="text-3xl font-bold text-purple-400">{result.old_concept}</p>
                </div>
                <div className="text-center text-gray-600">↓</div>
                <div>
                  <p className="text-xs font-medium text-gray-400 mb-2">NEW CONCEPT (SECTION {result.new_section})</p>
                  <p className="text-3xl font-bold text-pink-400">{result.new_concept}</p>
                </div>
                <div className="mt-6 pt-6 border-t border-white/10">
                  <p className="text-xs font-medium text-gray-400 mb-3">IMPACT</p>
                  <p className="text-gray-300">{result.impact}</p>
                </div>
              </div>
            </div>
          )}

          {result.type === 'form' && (
            <div className="bg-gradient-to-br from-orange-500/10 to-yellow-500/10 border border-orange-500/20 rounded-2xl p-8">
              <h3 className="text-lg font-semibold mb-8 text-white">Form Mapping</h3>
              <div className="grid grid-cols-2 gap-6 mb-6">
                <div className="bg-white/5 rounded-lg p-6 border border-white/10">
                  <p className="text-xs font-medium text-gray-400 mb-2">OLD FORM</p>
                  <p className="text-2xl font-bold text-orange-400 font-mono">{result.old_form}</p>
                </div>
                <div className="bg-white/5 rounded-lg p-6 border border-white/10">
                  <p className="text-xs font-medium text-gray-400 mb-2">NEW FORM</p>
                  <p className="text-2xl font-bold text-yellow-400 font-mono">{result.new_form}</p>
                </div>
              </div>
              <div className="pt-6 border-t border-white/10">
                <p className="text-xs font-medium text-gray-400 mb-3">PURPOSE</p>
                <p className="text-gray-300 mb-4">{result.purpose}</p>
                <span className="inline-block px-3 py-1 bg-green-500/10 rounded-full text-xs text-green-400">
                  {result.status}
                </span>
              </div>
            </div>
          )}
        </div>
      )}

      {result && !result.found && (
        <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-6 text-yellow-300 text-sm">
          <p className="font-medium mb-1">Not found</p>
          <p>Try the Assistant tab to ask about "{result.old_section}"</p>
        </div>
      )}
    </div>
  )
}
