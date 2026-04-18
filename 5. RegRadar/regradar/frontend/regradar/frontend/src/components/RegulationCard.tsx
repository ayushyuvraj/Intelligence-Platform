import { Calendar, Building2 } from 'lucide-react';

interface Regulation {
  id: string;
  title: string;
  summary: string;
  source_body: string;
  impact_level: 'HIGH' | 'MEDIUM' | 'LOW';
  published_date: string;
  source_url: string;
}

const impactColors = {
  HIGH: 'bg-red-100 text-red-800',
  MEDIUM: 'bg-yellow-100 text-yellow-800',
  LOW: 'bg-green-100 text-green-800',
};

const RegulationCard = ({ regulation, onClick }: { regulation: Regulation; onClick?: () => void }) => (
  <div className="border rounded-lg p-4 hover:shadow-lg transition cursor-pointer" onClick={onClick}>
    <div className="flex justify-between items-start mb-2">
      <h3 className="font-semibold text-lg flex-1">{regulation.title}</h3>
      <span className={`px-3 py-1 rounded text-sm font-medium ${impactColors[regulation.impact_level]}`}>
        {regulation.impact_level}
      </span>
    </div>
    <p className="text-gray-600 text-sm mb-3">{regulation.summary}</p>
    <div className="flex gap-4 text-xs text-gray-500">
      <div className="flex items-center gap-1">
        <Building2 size={14} />
        {regulation.source_body}
      </div>
      <div className="flex items-center gap-1">
        <Calendar size={14} />
        {new Date(regulation.published_date).toLocaleDateString()}
      </div>
    </div>
    <a
      href={regulation.source_url}
      target="_blank"
      rel="noopener noreferrer"
      className="text-blue-600 text-xs mt-3 block hover:underline"
    >
      View Original →
    </a>
  </div>
);

export default RegulationCard;
