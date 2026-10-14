---
name: registrar-no-mvp
description: Registra no MVP Experts o trabalho feito na sessão (projeto, tarefas e horas no timesheet) pela API. Use quando o usuário pedir para registrar, cadastrar, lançar horas, apontar horas ou apontar o que foi feito no MVP Experts.
---

# Registrar no MVP Experts

Cliente: `python3 ~/.claude/skills/registrar-no-mvp/mvp_api.py [--instancia NOME] <comando>`
(saída JSON no stdout; erro no stderr com código 1; sem configuração, código 2).
Veja os comandos com `--help` e `<comando> --help`.

Configuração em `~/.config/mvp-experts/<instancia>.env` (padrão `api`) ou nas variáveis
MVP_API_URL / MVP_API_TOKEN. **Nunca** leia, imprima ou peça o token. Se o cliente sair com
código 2, repasse a instrução ao usuário e pare; não tente contornar.

## Passo a passo

0. **Contexto**: leia `ROTINA.md` (nesta pasta) para saber a rotina, as máquinas e qual
   projeto corresponde a cada frente (BENTEC, IFRS, Conexão G). Para ver o que já foi lançado
   num dia, de qualquer máquina, use `dia [AAAA-MM-DD]`.
1. **Instância e usuário**: liste `ls ~/.config/mvp-experts/*.env`. Se houver mais de uma e o
   usuário não disse qual, pergunte antes de gravar. Rode `eu` e confirme nome e instituições.
2. **Projeto**: `projetos --q "<termo>"` (tente também `--meus`).
   - Um candidato claro: use.
   - Vários: pergunte qual.
   - Nenhum: crie com `projeto-criar`, com título, descrição e objetivo curtos em português do
     Brasil, tirados do pedido. Instituição vem de `eu`: uma só, use; várias, pergunte.
3. **Tarefas**: antes de criar, `tarefas PROJETO --q "<termo>"` para não duplicar.
   - Uma tarefa por entrega; título curto no imperativo ("Corrigir login por SSO").
   - Descrição com o que foi feito e por quê (inclua hash do commit, se houver).
   - Use `--eu` para atribuir a mim.
   - Terminada: `tarefa-status TAREFA --status done`.
4. **Horas — nunca invente**:
   - Trabalho em andamento: `iniciar PROJETO --tarefa ID` no começo e `parar` no fim.
   - Trabalho já feito: `horas PROJETO --tarefa ID --inicio "AAAA-MM-DD HH:MM"` com `--fim` real
     ou `--minutos` informados pelo usuário. Se não souber quanto tempo levou, **pergunte**.
   - Horários sem fuso valem em America/Sao_Paulo. Máximo de 24 h por lançamento.
   - Iniciar cronômetro encerra o que estiver rodando: confira `rodando` antes, se fizer sentido.
   - `iniciar` e `horas` acrescentam `[MVP_MAQUINA]` (ou o hostname) à descrição. Não repita.
5. **Resumo final**: liste o que foi criado ou lançado, com ids e links (`url` das saídas).

## Limites

- Não apague nem edite nada que não tenha sido criado nesta sessão.
- 403 em tarefa: o usuário provavelmente não é membro ativo do projeto (convite pendente).
- Projeto finalizado/cancelado recusa cronômetro; use `horas`.
