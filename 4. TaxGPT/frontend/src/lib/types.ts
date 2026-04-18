// API Response Types
export interface HealthResponse {
  status: string
  index_ready: boolean
  provider: string
}

export interface ChatMessage {
  question: string
  answer: string
}

export interface Source {
  source: string
  section?: string
}

export interface QAResponse {
  answer: string
  error: boolean
  sources: Source[]
  filtered: boolean
}

export interface MapperRequest {
  section: string
}

export interface SectionResult {
  found: true
  type: 'section'
  old_section: string
  new_section: string
  title_old: string
  title_new: string
  change_summary: string
  category: string
}

export interface ConceptResult {
  found: true
  type: 'concept'
  old_concept: string
  new_concept: string
  new_section: string
  change_summary: string
  impact: string
}

export interface FormResult {
  found: true
  type: 'form'
  old_form: string
  new_form: string
  purpose: string
  status: string
}

export interface NotFoundResult {
  found: false
  old_section: string
}

export type MapperResponse = SectionResult | ConceptResult | FormResult | NotFoundResult

export interface MapperStatsResponse {
  total_old_to_new: number
  total_concepts: number
  total_forms: number
}

export interface ProfileItem {
  id: string
  label: string
}

export interface ProfileListResponse {
  profiles: ProfileItem[]
}

export interface ProfileResponse {
  profile: string
  label: string
  analysis: string
  source: string
  error: boolean
}

export interface NoticeMetadata {
  notice_type?: string
  sections: string[]
  dates: string[]
  severity?: string
}

export interface NoticeResponse {
  analysis: string
  source: string
  error: boolean
  metadata?: NoticeMetadata
}

export interface IngestionStatusResponse {
  status: string
  progress_pct: number
  message: string
  log_tail: string[]
  started_at?: string
  completed_at?: string
}
