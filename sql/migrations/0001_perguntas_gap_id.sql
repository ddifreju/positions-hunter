-- Fase 3: liga a pergunta da Entrevista 2 ao gap tipo "documentacao" que
-- ela tenta resolver. Sem isso não dá pra saber qual gap fechar quando a
-- resposta chega (pode ser dias depois, então não dá pra confiar em
-- estado em memória).
alter table perguntas add column gap_id uuid references gaps(id);
