-- Drop and recreate documents table with all new fields
drop table if exists documents cascade;

create table documents (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references users(id) on delete cascade,
  filename text not null,
  document_type text,
  extracted_text text,
  -- Core analysis
  summary text,
  risk_level text,
  risk_reason text,
  document_status text default 'Needs Review',
  confidence_score integer default 0,
  final_verdict text,
  safe_to_sign boolean default false,
  -- Issue arrays
  document_issues text[],
  warnings text[],
  suspicious_clauses text[],
  missing_clauses text[],
  financial_risks text[],
  expiry_risks text[],
  unfair_conditions text[],
  compliance_issues text[],
  privacy_risks text[],
  legal_loopholes text[],
  recommendations text[],
  -- Metadata
  created_at timestamptz default now()
);

-- Disable RLS
alter table documents disable row level security;
grant all on documents to anon, authenticated, service_role;
