import { useParams, useNavigate } from 'react-router-dom';
import { regulationApi } from '../api/client';
import { useState, useEffect } from 'react';
import { ArrowLeft, FileText, AlertTriangle, CheckCircle, ExternalLink, Info } from 'lucide-react';

const DetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [reg, setReg] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchDetail() {
      try {
        if (!id) return;
        const data = await regulationApi.fetchRegulationDetail(id, '');
        setReg(data);
      } catch (e) {
        console.error("Error fetching regulation detail", e);
      } finally {
        setLoading(false);
      }
    }
    fetchDetail();
  }, [id]);

  if (loading) return <div className="p-8 text-center">Loading analysis...</div>;
  if (!reg) return <div className="p-8 text-center">Regulation not found.</div>;

  const impactColor = {
    HIGH: 'text-impact-high bg-impact-high/10',
    MEDIUM: 'text-impact-medium bg-impact-medium/10',
    LOW: 'text-impact-low bg-impact-low/10'
  }[reg.ai_impact_level as 'HIGH' | 'MEDIUM' | 'LOW'] || 'text-gray-500 bg-gray-100';

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <button
        onClick={() => navigate('/')}
        className="flex items-center gap-2 text-sm text-brand-muted hover:text-brand-dark mb-6 transition-colors"
      >
        <ArrowLeft size={16} /> Back to Feed
      </button>

      <div className="bg-white rounded-2xl border border-brand-muted/20 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-brand-muted/10 bg-brand-light/50">
          <div className="flex justify-between items-start mb-4">
            <span className={`px-3 py-1 rounded-full text-xs font-bold ${impactColor}`}>
              {reg.ai_impact_level} IMPACT
            </span>
            <span className="text-xs text-brand-muted">{reg.original_date}</span>
          </div>
          <h1 className="text-2xl font-bold text-brand-dark mb-2">{reg.ai_title}</h1>
          <div className="flex items-center gap-2 text-sm text-brand-muted">
            <FileText size={14} /> {reg.source_body} | Official Notification
          </div>
        </div>

        <div className="p-6 space-y la-8">
          <section>
            <div className="flex items-center gap-2 mb-3 text-brand-dark font-bold">
              <Info size={18} className="text-brand-accent" />
              <h2>Executive Summary (TL;DR)</h2>
            </div>
            <p className="text-brand-muted leading-relaxed bg-brand-light p-4 rounded-lg border-l-4 border-brand-accent">
              {reg.ai_tldr}
            </p>
          </section>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <section className="p-4 rounded-xl border border-brand-muted/20 bg-white">
              <div className="flex items-center gap-2 mb-3 text-brand-dark font-bold">
                <AlertTriangle size={18} className="text-impact-medium" />
                <h3>What Changed?</h3>
              </div>
              <p className="text-sm text-brand-muted leading-relaxed">
                {reg.ai_what_changed}
              </p>
            </section>

            <section className="p-4 rounded-xl border border-brand-muted/20 bg-white">
              <div className="flex items-center gap-2 mb-3 text-brand-dark font-bold">
                <CheckCircle size={18} className="text-green-500" />
                <h3>Action Required</h3>
              </div>
              <div className="text-sm text-brand-muted space-y-2">
                {(reg.ai_action_required || '').split('\n').map((item: string, i: number) => (
                  <div key={i} className="flex gap-2">
                    <span className="text-brand-accent">•</span> {item}
                  </div>
                ))}
              </div>
            </section>
          </div>

          <section className="pt-6 border-t border-brand-muted/10">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-brand-muted uppercase tracking-wider">Source Documentation</h3>
              <a
                href={reg.source_url}
                target="_blank"
                className="flex items-center gap-1 text-sm font-medium text-brand-accent hover:underline"
              >
                View Original PDF <ExternalLink size={14} />
              </a>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};

export default DetailPage;
