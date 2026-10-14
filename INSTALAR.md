# Instalar a skill registrar-no-mvp numa máquina nova

1. Clone o repositório (privado) na pasta de skills do usuário:

       git clone https://github.com/giovanebertol/claude-skill-registrar-no-mvp.git ~/.claude/skills/registrar-no-mvp

   Para atualizar depois, rode `git -C ~/.claude/skills/registrar-no-mvp pull`.

2. Gere uma chave **própria desta máquina**: no MVP Experts, Integrações > Gerar Nova Chave API.

3. Crie a configuração (fora do repositório) e edite o arquivo para colar o token:

       mkdir -p ~/.config/mvp-experts && chmod 700 ~/.config/mvp-experts
       printf 'MVP_API_URL=https://mvpexperts.conexaogtecnologia.com.br/api\nMVP_API_TOKEN=\nMVP_MAQUINA=bentec\n' > ~/.config/mvp-experts/api.env
       chmod 600 ~/.config/mvp-experts/api.env
       nano ~/.config/mvp-experts/api.env

4. Confira com `python3 ~/.claude/skills/registrar-no-mvp/mvp_api.py eu`.

5. Opcional: para não ser interrompido a cada chamada, coloque no `~/.claude/settings.json`:

       "permissions": { "allow": ["Bash(python3 ~/.claude/skills/registrar-no-mvp/mvp_api.py:*)"] }

No Windows sem WSL, use `python` no lugar de `python3` e `%USERPROFILE%\.claude\skills\…`.
O cliente lê `~/.config/mvp-experts/` também no Windows (`C:\Users\<você>\.config\mvp-experts\`).
