import React, { useEffect, useState } from 'react';
import { regulationApi } from './api/client';
import { useAppStore } from './store/useAppStore';
import RegulationCard from './components/RegulationCard';
import { Filter, Search, Loader2 } from 'lucide-react';

const FeedPage = () => {
  const { sessionId, setSessionId, selectedDomains } = useAppStore();
  const [regs, setRegs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ source: '', impact: '', query: '' });
  const [domains, setDomains] = useState<string[]>([]);

  useEffect(() => {
    async function init() {
      try {
        const domainData = await regulationApi.fetchDomains();
        setDomains(domainData.domains.map((d: any) => d.name));

        if (!sessionId) {
          const session = await regulationApi.createSession(selectedDomains);
          setSessionId(session.session_id);
        }

        fetchFeed();
      } catch (e) {
        // Session initialization error - UI error handling will display to user
      } finally {
        setLoading(false);
      }
    }
    init();
  }, [sessionId]);

  async function fetchFeed() {
    setLoading(true);
    try {
      const data = sessionId
        ? await regulationApi.fetchMyFeed(sessionId, { ...filters })
        : await regulationApi.fetchRegulations({ ...filters });
      setRegs(data.regulations);
    } catch (e) {
      // Feed fetch error - UI error handling will display to user
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <header className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-brand-dark">Regulatory Feed</h1>
          <p className="text-brand-muted">Real-time intelligence from SEBI & RBI</p>
        </div>

        <div className="flex gap-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-brand-muted" size={18} />
            <input
              className="pl-10 pr-4 py-2 border border-brand-muted/30 rounded-lg text-sm focus:ring-2 focus:ring-brand-accent outline-none w-full md:w-64"
              placeholder="Search regulations..."
              onChange={(e) => {
                setFilters(prev => ({ ...prev, query: e.target.value }));
              }}
            />
          </div>
          <button
            onClick={fetchFeed}
            className="p-2 bg-brand-dark text-white rounded-lg hover:bg-brand-primary transition-colors"
          >
            <Filter size={20} />
          </button>
        </div>
      </header>

      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 gap-4">
          <Loader2 className="animate-spin text-brand-accent" size={40} />
          <p className="text-brand-muted animate-pulse">Fetching latest intelligence...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {regs.length > 0 ? (
            regs.map(reg => (
              <RegulationCard key={reg.id} regulation={reg} onClick={() => {}} />
            ))
          ) : (
            <div className="col-span-full text-center py-20 text-brand-muted">
              No regulations found matching your filters.
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FeedPage;
