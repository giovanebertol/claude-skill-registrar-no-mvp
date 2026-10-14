# Rotina e mapa de trabalho do Giovane

Arquivo compartilhado entre as máquinas (vai no repositório da skill). Sem segredos aqui.
Atualize este arquivo, e não a memória local, quando a rotina ou os projetos mudarem.

## Quem
Giovane da Silva Bertol — MVP Experts: giovane.bertol@conexaogtecnologia.com.br (usuário 6).
Commits no IFRS: `giovane.bertol@ifrs.edu.br`.

## Rotina (padrão; é irregular, confirme horários antes de lançar)
| Quando | Onde | Instituição no MVP |
|---|---|---|
| Seg a qua, ~07:00–12:00 | BENTEC | 6 (BENTEC) |
| Tarde, ~13:00–17:00 | IFRS — CSI, coordenador de sistemas | 1 (IFRS) |
| Noite, às vezes | BENTEC, IFRS ou Conexão G | 6, 1 ou 9 (CGTECH) |

## Máquinas
Trabalha em 3 computadores nos mesmos repositórios. As sessões do Claude Code e as alterações
sem commit de um computador não aparecem nos outros. Cada máquina tem a própria chave de API e
um nome em `MVP_MAQUINA`, que vai nos lançamentos de horas.
| MVP_MAQUINA | Hostname | Onde fica |
|---|---|---|
| casa? | DESKTOP-J8KSO7E | (preencher) |
| bentec | (preencher) | BENTEC |
| (preencher) | (preencher) | (preencher) |

## Projetos no MVP Experts
| Frente | Projeto (id) | Repositórios / pistas |
|---|---|---|
| IFRS | SISPS (36) | gitlab.ifrs.edu.br/dti/sisps |
| IFRS | Pulso (40) | github.com/giovanebertol/pulso — CPA, avaliação institucional |
| IFRS | Projeto IFRS 2026 (35) | demais sistemas da DTI (api-de-servicos, sistemas_ifrs, suite…) |
| IFRS | IFRS - DTI (39) | |
| BENTEC | Bentec Intranet (42) | |
| Conexão G | Contrato Mensalidade Assif (43) | |
| Conexão G | Chamados 2026 (41) | |
| Conexão G | Backlog de melhorias MVP Experts (37) | |
| ? | Pedium — portal de pedidos | ainda sem projeto; confirmar a frente |

## Como descobrir o que foi feito num dia
1. `mvp_api.py dia AAAA-MM-DD`: o que já foi lançado, de qualquer máquina (fonte única).
2. `git fetch --all` e `git log --all --since=... --author=giovane` nos repositórios: commits de todas as máquinas.
3. Sessões do Claude Code em `~/.claude/projects/*/*.jsonl`: só desta máquina.
4. Se ainda faltar algo (reuniões, outra máquina sem push), pergunte.
