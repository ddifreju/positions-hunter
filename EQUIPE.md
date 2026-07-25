# Equipe de agentes — MatchVagas

Time inicial de 3, conforme Seção 4.1 do briefing. Um quarto agente (`curador`) só seria criado se a curadoria da Seção 5 rendesse mais de 5 candidatos a avaliar — rendeu 4 (um deles "não localizado"), então a curadoria foi feita diretamente pelo tech lead, sem criar o agente.

## arquiteto (`.claude/agents/arquiteto.md`)
Sênior. Schema, contratos entre módulos, decisões de stack, revisão antes do merge, poder de veto sobre R1/R2/R4/R5. Nunca escreve implementação.

## construtor (`.claude/agents/construtor.md`)
Pleno. Implementação — conectores, ETL, matching, telas, geração de CV. Entrega código e teste juntos.

## validador (`.claude/agents/validador.md`)
Júnior. Roda testes, checa APIs externas, procura chave vazada no diff, verifica conformidade da R2 na saída do gerador de CV. Só reporta, não corrige.

## Justificativa de cada agente criado

- Os três agentes acima foram criados exatamente como especificado na Seção 4.2 do briefing — nenhum critério adicional de dimensionamento foi necessário, já que o time inicial de 3 é o ponto de partida definido, não algo a ser justificado caso a caso.

## Próxima revisão

Reavaliar a necessidade do `curador` ao fim de cada fase, se a curadoria contínua (Seção 5.4) acumular candidatos suficientes para justificar um quarto agente.
