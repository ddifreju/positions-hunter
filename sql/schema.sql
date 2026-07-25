-- Schema inicial do MatchVagas (Seção 7.3 do briefing).
-- Rascunho para revisão do agente `arquiteto` antes de aplicar no Supabase.
-- Copiado do briefing sem alterações; ajustes ficam registrados aqui pelo arquiteto.

create table usuarias (
  id uuid primary key default gen_random_uuid(),
  nome text not null,
  criado_em timestamptz default now()
);

create table documentos (
  id uuid primary key default gen_random_uuid(),
  usuaria_id uuid references usuarias(id) on delete cascade,
  tipo text check (tipo in ('cv','linkedin','certificado','portfolio','outro')),
  nome_arquivo text,
  storage_path text,
  texto_extraido text,
  criado_em timestamptz default now()
);

create table evidencias (
  id uuid primary key default gen_random_uuid(),
  usuaria_id uuid references usuarias(id) on delete cascade,
  texto text not null,
  tags text[] not null default '{}',
  fonte text check (fonte in ('documento','entrevista','gap_resolvido')),
  documento_id uuid references documentos(id),
  criado_em timestamptz default now()
);

create table vagas (
  id uuid primary key default gen_random_uuid(),
  plataforma text not null,
  id_externo text not null,
  titulo text,
  empresa text,
  descricao text,
  url_candidatura text,
  modalidade text,
  localizacao text,
  coletada_em timestamptz default now(),
  unique (plataforma, id_externo)
);

create table candidaturas (
  id uuid primary key default gen_random_uuid(),
  usuaria_id uuid references usuarias(id) on delete cascade,
  vaga_id uuid references vagas(id),
  status text check (status in
    ('descoberta','interesse','cv_gerado','enviada','triagem','entrevista','oferta','recusada')),
  score numeric,
  justificativa_score text,
  cv_storage_path text,
  atualizado_em timestamptz default now(),
  unique (usuaria_id, vaga_id)
);

create table gaps (
  id uuid primary key default gen_random_uuid(),
  usuaria_id uuid references usuarias(id) on delete cascade,
  skill text not null,
  tipo text check (tipo in ('documentacao','competencia')),
  frequencia int default 1,
  status text check (status in ('aberto','em_estudo','resolvido')) default 'aberto',
  evidencia_resolvida_id uuid references evidencias(id),
  atualizado_em timestamptz default now(),
  unique (usuaria_id, skill)
);

create table perguntas (
  id uuid primary key default gen_random_uuid(),
  usuaria_id uuid references usuarias(id) on delete cascade,
  rodada int not null,
  texto text not null,
  resposta text,
  respondida_em timestamptz,
  gerou_evidencia_id uuid references evidencias(id),
  -- adicionada na Fase 3 (ver sql/migrations/0001_perguntas_gap_id.sql):
  -- liga a pergunta ao gap tipo "documentacao" que ela tenta resolver,
  -- necessario para fechar o gap certo quando a resposta chega.
  gap_id uuid references gaps(id)
);
