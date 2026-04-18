import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { regulationApi } from '../api/client';
import { useAppStore } from '../store/useAppStore';
import { useState, useEffect } from 'react';

const StatsDashboard = () => {
  const { sessionId } = useAppStore();
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStatsData() {
      try {
        if (!sessionId) return;
        const data = await regulationApi.fetchStats(sessionId);
        setStats(data);
      } catch (e) {
        console.error("Stats error", e);
      } finally {
        setLoading(false);
      }
    }
    fetchStatsData();
  }, [sessionId]);

  if (loading) return <div className="p-8 text-center">Loading Analytics...</div>;
  if (!stats) return <div className="p-8 text-center">No stats available.</div>;

  const COLORS = ['#ef4444', '#f59e0b', '#3b82f6'];

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-2xl border border-brand-muted/20 shadow-sm">
          <span className="text-sm text-brand-muted">Total Regulations</span>
          <div className="text-3xl font-bold text-brand-dark">{stats.total_regulations}</div>
        </div>
        <div className="bg-white p-6 rounded-2xl border border-brand-muted/20 shadow-sm">
          <span className="text-sm text-brand-muted">Last Updated</span>
          <div className="text-lg font-medium text-brand-dark">{new Date(stats.last_updated).toLocaleDateString()}</div>
        </div>
        <div className="bg-white p-6 rounded-2xl border border-brand-muted/20 shadow-sm">
          <span className="text-sm text-brand-muted">Sources Monitored</span>
          <div className="text-3xl font-bold text-brand-dark">{Object.keys(stats.by_source).length}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded-2xl border border-brand-muted/20 shadow-sm">
          <h3 className="text-lg font-bold text-brand-dark mb-6">Regulatory Volume (30 Days)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={stats.trends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="date" fontSize={12} tickMargin={10} stroke="#94a3b8" />
                <YAxis fontSize={12} stroke="#94a3b8" />
                <Tooltip />
                <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-brand-muted/20 shadow-sm">
          <h3 className="text-lg font-bold text-brand-dark mb-6">Impact Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={Object.entries(stats.by_impact).map(([name, value]) => ({ name, value }))}
                  cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value"
                >
                  {Object.entries(stats.by_impact).map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatsDashboard;
