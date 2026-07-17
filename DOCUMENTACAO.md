# 📘 ABM TI — Documentação do Sistema

---

# PARTE 1 — Visão Geral (para Coordenador)

---

## 1. Visão Geral

Sistema web completo para gestão de TI com **8 módulos internos** + **1 portal público** para funcionários abrirem chamados.

---

## 2. Stack Tecnológica

| Camada | Tecnologia |
|---|---|
| **Backend** | Python 3.11 + Django 4.2 |
| **Frontend** | Bootstrap 5.3 + Chart.js + FullCalendar |
| **Banco** | PostgreSQL 15 |
| **Infra** | Docker + Docker Compose (dev: runserver, prod: Gunicorn + Nginx) |
| **Relatórios** | WeasyPrint (PDF) + QuickChart (gráficos) |

---

## 3. Arquitetura — 9 Apps Django

```
sistema_chamados_ti/
├── core/           # Config, middleware, login, template base
├── dashboard/      # Tela inicial com visão geral
├── chamados/       # 🎫 Gestão de chamados
├── inventario/     # 🖥️ Controle de equipamentos
├── conhecimento/   # 📚 Base de conhecimento
├── tarefas/        # 📋 Quadro Kanban
├── calendario/     # 📅 Agenda de eventos
├── relatorios/     # 📊 Gráficos e exportação (PDF/CSV)
├── usuarios/       # 👥 Gestão de usuários
├── portal/         # 🌐 Portal do funcionário (abrir chamados)
├── static/         # CSS + JS
└── media/          # Uploads (imagens de chamados/equipamentos)
```

---

## 4. Controle de Acesso

```
┌────────────┐     is_staff=True      ┌────────────┐
│   Login    │ ──────────────────────→ │   Sistema  │
│  (único)   │                         │  (8 apps)  │
└────────────┘     is_staff=False     └────────────┘
       │  ───────────────────────────→ ┌────────────┐
       └──────────────────────────────→│   Portal   │
                                       │ (abrir chamados)│
                                       └────────────┘
```

- **`is_staff=True`** → acessa o sistema completo
- **`is_staff=False`** → vai direto pro portal (só abre chamados e vê os seus)
- Middleware `StaffRequiredMiddleware` bloqueia acesso indevido às rotas do sistema

---

## 5. Cada Módulo em Detalhe

### Dashboard (`/`)
Cartões com contadores em tempo real:
- Chamados abertos, críticos, equipamentos ativos, eventos do dia
- Tabela de chamados recentes + tarefas pendentes
- Auto-refresh a cada 15 segundos via AJAX
- Toast de notificação quando chega chamado novo

### Chamados (`/chamados/`)
- CRUD completo com formulário de criação/edição
- Filtros por status, prioridade, categoria + busca textual
- Ao criar: **Setor** e **Solicitante** são dropdowns — setor filtra quem aparece como solicitante
- Ao editar: título, descrição, solicitante e setor ficam **travados** (não podem ser alterados)
- Status "Resolvido" trava o chamado (não pode mais editar)
- Confirmação JS ao resolver (evita clique acidental)
- Histórico de alterações registrado automaticamente
- Notificação por email ao criar chamado (signal Django)
- Imagens separadas: `imagem_solicitante` (anexada pelo usuário) vs `imagem_tecnica` (anexada pelo TI)
- Badges coloridos: Baixa (verde), Média (azul), Alta (laranja), Crítica (vermelha)

### Inventário (`/inventario/`)
- CRUD de equipamentos (patrimônio, hostname, marca, modelo, specs)
- **Setor** com 14 opções fixas (APOIO, ATENDIMENTO, T.I, RH...)
- **Responsável** — FK para User, filtrado dinamicamente por setor
- Campo de **imagem** (foto do equipamento/NF)
- Status com badges: Ativo (verde), Manutenção (laranja), Inativo (cinza), Descartado (vermelho)
- Histórico detalhado: registra **cada campo alterado** com valor antigo e novo

### Base de Conhecimento (`/conhecimento/`)
- Artigos com título, conteúdo, categoria e autor
- Sidebar com filtro por categoria + criação inline de categorias
- Contador de visualizações por artigo
- Ordenação por mais visualizados
- Tags removidas (eram sem utilidade)

### Tarefas (`/tarefas/`)
- Quadro Kanban com 3 colunas: A Fazer, Em Andamento, Concluído
- Criar via modal, mover entre colunas, editar, excluir
- Limite de 50/50/20 por coluna
- Responsável filtrado: só usuários do setor T.I
- Nome completo no dropdown (não username)

### Calendário (`/calendario/`)
- FullCalendar com visualização mensal
- Eventos com tipo (Manutenção, Visita, Backup...) e prioridade
- Cor do evento baseada na prioridade
- Navegação rápida: selects de mês + botões `◀ ▶` de ano
- Sidebar com próximos eventos

### Relatórios (`/relatorios/`)
- Filtros: mês, ano, setor
- 3 cards de stats: Total de Chamados, Resolvidos, Taxa de Resolução
- 4 gráficos (Chart.js com tema escuro):
  - Produtividade Mensal (linha, largura total)
  - Chamados por Categoria (doughnut/pizza)
  - Top Solicitantes (barra horizontal)
  - Equipamentos por Categoria (barra)
- Tabela com todos os chamados do mês
- **Exportar CSV** (delimitador `;` pra Excel pt-BR, BOM UTF-8 pra acentos)
- **Enviar PDF** por email (WeasyPrint + QuickChart)
- Dark tooltips nos gráficos

### Usuários (`/usuarios/`)
- CRUD de usuários (User Django + Perfil)
- Perfil: setor (14 opções), ramal, avatar
- Badges coloridos: Admin Sim (verde), Admin Não (cinza), Ativo Sim (verde), Ativo Não (vermelho)
- Filtro por setor (abre em T.I por padrão)
- **Cargo removido** — `is_staff` define tudo

### Portal (`/portal/`)
- Tela limpa com navbar + formulário de abrir chamado
- Campos: Título, Descrição, Imagem (opcional)
- "Meus Chamados" com paginação (10 por página)
- Detalhe do chamado com resposta do técnico
- Auto-refresh do contador a cada 15s
- Layout isolado (não usa o sidebar do sistema)

---

## 6. Funcionalidades Transversais

| Funcionalidade | Como funciona |
|---|---|
| **Badges coloridos** | Padronizados em 5 cores (verde, azul, laranja, vermelho, cinza) com fundo translúcido + texto vivo |
| **Sidebar colapsável** | 3 seções (Principal, Ferramentas, Administração) com toggle — estado salvo em localStorage |
| **Tema escuro** | 100% dark mode com paleta GitHub (`#0d1117`/`#161b22`/`#30363d`) + navbar em gradiente `#0e1d38 → #0c1b33` |
| **Pagination** | Botões numerados `‹ 1 2 3 ›` em todas as listagens |
| **Auto-refresh** | Dashboard e portal atualizam via AJAX a cada 15s |
| **XSS Protection** | Escape HTML no JavaScript do auto-refresh |
| **CSV Export** | Delimitador `;` + BOM UTF-8 → abre direto no Excel |
| **Email** | Signal Django notifica ao criar chamado; PDF enviado via WeasyPrint |
| **Migrations** | 1 `0001_initial.py` por app (limpas, sem histórico) |

---

## 7. Docker

```
Dev:  docker compose up        → Django runserver (auto-reload)
Prod: docker compose -f docker-compose.prod.yml up  → Gunicorn + Nginx
```

Containers: `web` (Django), `db` (PostgreSQL), `nginx` (só prod)

---

## 8. Variáveis de Ambiente (`.env`)

```
DEBUG=True/False
SECRET_KEY=...
DB_NAME=sistema_ti  DB_USER=admin  DB_PASSWORD=...
DB_HOST=db  DB_PORT=5432
ALLOWED_HOSTS=...
SITE_URL=http://...
EMAIL_HOST=smtp.gmail.com  EMAIL_HOST_USER=...  EMAIL_HOST_PASSWORD=...
NOTIFICACAO_EMAIL=ti@empresa.com.br
RELATORIO_EMAIL=relatorios@abmti.com.br
```

---

# PARTE 2 — Documentação Técnica

---

## 1. BANCO DE DADOS — Todas as Tabelas

### Tabela: `auth_user` (Usuários — built-in Django)

| Coluna | Tipo | Descrição |
|---|---|---|
| `id` | PK (INT) | |
| `username` | VARCHAR(150) | Nome de login |
| `first_name` | VARCHAR(150) | Nome |
| `last_name` | VARCHAR(150) | Sobrenome |
| `email` | VARCHAR(254) | |
| `is_staff` | BOOLEAN | **True = acessa o sistema, False = portal** |
| `is_active` | BOOLEAN | Usuário ativo |
| `password` | VARCHAR(128) | Hash da senha |

---

### Tabela: `usuarios_perfil` (Perfil do Usuário)

**1:1 com `auth_user`** — Um usuário tem um perfil.

| Coluna | Tipo | FK | Descrição |
|---|---|---|---|
| `id` | PK | | |
| `usuario_id` | FK | → auth_user | OneToOneField |
| `setor` | VARCHAR(100) | | 14 opções fixas (APOIO, T.I, RH...) |
| `telefone` | VARCHAR(20) | | Ramal |
| `avatar` | VARCHAR(100) | | Foto de perfil |

---

### Tabela: `chamados_chamado` (Chamados)

| Coluna | Tipo | FK | Descrição |
|---|---|---|---|
| `id` | PK | | Nº do chamado |
| `titulo` | VARCHAR(200) | | |
| `descricao` | TEXT | | |
| `solicitante` | VARCHAR(150) | | Nome do solicitante |
| `setor` | VARCHAR(100) | | 14 opções fixas |
| `categoria` | VARCHAR(20) | | Hardware/Software/Rede/E-mail/Impressora/Outro |
| `prioridade` | VARCHAR(10) | | Baixa/Média/Alta/Crítica |
| `status` | VARCHAR(15) | | Aberto/Em Andamento/Resolvido |
| `tecnico_id` | FK | → auth_user | Técnico responsável (pode ser nulo) |
| `observacoes` | TEXT | | Anotações do técnico |
| `imagem_tecnica` | VARCHAR(100) | | Imagem anexada pelo TI |
| `imagem_solicitante` | VARCHAR(100) | | Imagem anexada pelo usuário |
| `criado_por_id` | FK | → auth_user | Quem criou |
| `criado_em` | DATETIME | | Data de criação (automático) |
| `atualizado_em` | DATETIME | | Última alteração (automático) |

---

### Tabela: `chamados_historicochamado` (Histórico dos Chamados)

**N:1 com `chamados_chamado`** — Um chamado tem vários registros de histórico.

| Coluna | Tipo | FK | Descrição |
|---|---|---|---|
| `id` | PK | | |
| `chamado_id` | FK | → chamados_chamado | |
| `usuario_id` | FK | → auth_user | Quem fez a ação |
| `acao` | VARCHAR(100) | | "Chamado criado", "Status alterado"... |
| `descricao` | TEXT | | "Status alterado de 'Aberto' para 'Em Andamento'" |
| `criado_em` | DATETIME | | |

---

### Tabela: `inventario_equipamento` (Inventário)

| Coluna | Tipo | FK | Descrição |
|---|---|---|---|
| `id` | PK | | |
| `patrimonio` | VARCHAR(50) | | Nº patrimônio (único) |
| `hostname` | VARCHAR(100) | | |
| `categoria` | VARCHAR(20) | | Computador/Notebook/Impressora/... |
| `marca` | VARCHAR(100) | | |
| `modelo` | VARCHAR(100) | | |
| `numero_serie` | VARCHAR(100) | | |
| `processador` | VARCHAR(200) | | |
| `memoria_ram` | VARCHAR(50) | | |
| `armazenamento` | VARCHAR(200) | | |
| `sistema_operacional` | VARCHAR(100) | | |
| `ip` | GENERIC_IP | | |
| `mac_address` | VARCHAR(50) | | |
| `setor` | VARCHAR(200) | | 14 opções fixas |
| `responsavel_id` | FK | → auth_user | Pessoa responsável (pode ser nulo) |
| `status` | VARCHAR(15) | | Ativo/Em Manutenção/Inativo/Descartado |
| `observacoes` | TEXT | | |
| `imagem` | VARCHAR(100) | | Foto do equipamento/NF |
| `criado_em` | DATETIME | | |
| `atualizado_em` | DATETIME | | |

---

### Tabela: `inventario_historicoequipamento` (Histórico do Inventário)

**N:1 com `inventario_equipamento`**

| Coluna | Tipo | FK | Descrição |
|---|---|---|---|
| `id` | PK | | |
| `equipamento_id` | FK | → inventario_equipamento | |
| `usuario_id` | FK | → auth_user | |
| `acao` | VARCHAR(100) | | "Equipamento cadastrado", "Equipamento atualizado" |
| `descricao` | TEXT | | "Setor alterado de 'Sala TI' para 'Financeiro'" |
| `criado_em` | DATETIME | | |

---

### Tabela: `tarefas_tarefa` (Tarefas)

| Coluna | Tipo | FK | Descrição |
|---|---|---|---|
| `id` | PK | | |
| `titulo` | VARCHAR(200) | | |
| `descricao` | TEXT | | |
| `prioridade` | VARCHAR(10) | | Baixa/Média/Alta/Crítica |
| `status` | VARCHAR(15) | | A Fazer/Em Andamento/Concluído |
| `responsavel_id` | FK | → auth_user | |
| `criado_por_id` | FK | → auth_user | |
| `prazo` | DATE | | Data limite |
| `criado_em` | DATETIME | | |
| `atualizado_em` | DATETIME | | |

---

### Tabela: `conhecimento_categoria` (Categorias da Base de Conhecimento)

| Coluna | Tipo | Descrição |
|---|---|---|
| `id` | PK | |
| `nome` | VARCHAR(100) | |
| `descricao` | TEXT | |
| `criado_em` | DATETIME | |

---

### Tabela: `conhecimento_artigo` (Artigos)

**N:1 com `conhecimento_categoria`**

| Coluna | Tipo | FK | Descrição |
|---|---|---|---|
| `id` | PK | | |
| `titulo` | VARCHAR(200) | | |
| `conteudo` | TEXT | | |
| `categoria_id` | FK | → conhecimento_categoria | |
| `autor_id` | FK | → auth_user | |
| `anexo` | VARCHAR(100) | | Arquivo anexo |
| `visualizacoes` | INT | | Contador de acessos |
| `criado_em` | DATETIME | | |
| `atualizado_em` | DATETIME | | |

---

### Tabela: `calendario_evento` (Eventos do Calendário)

| Coluna | Tipo | FK | Descrição |
|---|---|---|---|
| `id` | PK | | |
| `titulo` | VARCHAR(200) | | |
| `descricao` | TEXT | | |
| `tipo` | VARCHAR(20) | | Manutenção/Visita Técnica/Backup/Vencimento/Reunião/Outro |
| `cor` | VARCHAR(7) | | Cor em hex (#0d6efd) |
| `data_inicio` | DATETIME | | |
| `data_fim` | DATETIME | | |
| `dia_todo` | BOOLEAN | | |
| `criado_por_id` | FK | → auth_user | |
| `criado_em` | DATETIME | | |

---

## 2. DIAGRAMA DE RELACIONAMENTOS

```
auth_user
    │
    ├── (1:1) ──→ usuarios_perfil
    │
    ├── (1:N) ──→ chamados_chamado (criado_por)
    ├── (1:N) ──→ chamados_chamado (tecnico)
    ├── (1:N) ──→ chamados_historicochamado (usuario)
    │
    ├── (1:N) ──→ inventario_equipamento (responsavel)
    ├── (1:N) ──→ inventario_historicoequipamento (usuario)
    │
    ├── (1:N) ──→ tarefas_tarefa (responsavel)
    ├── (1:N) ──→ tarefas_tarefa (criado_por)
    │
    ├── (1:N) ──→ conhecimento_artigo (autor)
    │
    └── (1:N) ──→ calendario_evento (criado_por)


chamados_chamado
    └── (1:N) ──→ chamados_historicochamado


inventario_equipamento
    └── (1:N) ──→ inventario_historicoequipamento


conhecimento_categoria
    └── (1:N) ──→ conhecimento_artigo
```

---

## 3. FLUXO DE DADOS — Exemplo: Criar Chamado

```
1. Usuário acessa:  GET /chamados/novo/
2. urls.py → chamados/views.py → chamado_create()
3. View: form = ChamadoForm() vazio
4. Template: renderiza form.html
5. Usuário preenche e submete: POST /chamados/novo/
6. View: form = ChamadoForm(request.POST, request.FILES)
7. form.is_valid() → valida dados contra as regras do Model
8. form.save() → INSERT INTO chamados_chamado (...)
9. HistoricoChamado.objects.create() → INSERT INTO chamados_historicochamado
10. Signal post_save dispara → envia email (chamados/signals.py)
11. redirect('chamados_list') → usuário vê a lista
```

---

## 4. ROTAS DO SISTEMA

| URL | View | Descrição |
|---|---|---|
| `/` | dashboard | Visão geral |
| `/chamados/` | chamados_list | Lista com filtros |
| `/chamados/novo/` | chamados_create | Novo chamado |
| `/chamados/<id>/` | chamados_detail | Visualizar |
| `/chamados/<id>/editar/` | chamados_edit | Editar |
| `/chamados/<id>/status/` | chamado_update_status | Mudar status (POST) |
| `/inventario/` | inventario_list | Lista com filtros |
| `/inventario/novo/` | inventario_create | Novo equipamento |
| `/inventario/<id>/` | inventario_detail | Visualizar |
| `/inventario/<id>/editar/` | inventario_edit | Editar |
| `/inventario/<id>/excluir/` | inventario_delete | Excluir |
| `/conhecimento/` | conhecimento_list | Lista de artigos |
| `/conhecimento/novo/` | conhecimento_create | Novo artigo |
| `/tarefas/` | tarefas_kanban | Quadro Kanban |
| `/tarefas/nova/` | tarefa_create | Nova tarefa |
| `/calendario/` | calendario_index | Calendário |
| `/calendario/eventos/` | eventos_json | API JSON dos eventos |
| `/relatorios/` | relatorios_index | Gráficos e tabela |
| `/relatorios/enviar/` | enviar_relatorio | Enviar PDF (POST) |
| `/relatorios/exportar/` | exportar_csv | Baixar CSV |
| `/usuarios/` | usuarios_list | Lista com filtro |
| `/usuarios/novo/` | usuario_create | Novo usuário |
| `/usuarios/perfil/` | perfil_edit | Editar meu perfil |
| `/portal/` | portal_index | Portal do funcionário |
| `/portal/stats/` | portal_stats | API JSON do contador |
| `/accounts/login/` | login | Tela de login |
| `/accounts/logout/` | logout | Sair |

---

## 5. SEGURANÇA

| Camada | Onde | Bloqueia o quê |
|---|---|---|
| **Login obrigatório** | `@login_required` em todas as views | Acesso sem autenticação |
| **Staff vs Portal** | `StaffRequiredMiddleware` (`core/middleware.py`) | Usuário sem `is_staff` tentando acessar `/chamados/`, `/inventario/` etc → redireciona pro portal |
| **Admin-only** | `@user_passes_test(is_admin)` em views de Usuários | Só staff gerencia usuários |
| **Só POST** | `@require_POST` em views de status/exclusão | Acesso via GET = erro 405 |
| **CSRF** | `{% csrf_token %}` em todos os formulários | Ataques cross-site |
| **XSS** | `_esc()` em JavaScript no dashboard e portal | Escape de HTML malicioso no auto-refresh |
| **HTTPS (produção)** | `SECURE_SSL_REDIRECT=True`, `SECURE_HSTS_SECONDS` | Força conexão segura |
| **Cookies seguros** | `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True` | Cookies só via HTTPS |

---

## 6. REGRAS DE NEGÓCIO PRINCIPAIS

| Regra | Onde |
|---|---|
| Chamado resolvido não pode ser editado | `chamados/views.py:chamado_edit` e `chamado_update_status` |
| Ao criar chamado, setor + solicitante só aparecem após selecionar setor | `chamados/forms.py` + JS no template |
| Ao editar chamado, título/descrição/solicitante/setor são travados | `chamados/forms.py` (disabled=True) |
| Histórico registra cada alteração de status | `chamados/views.py` e `chamado_update_status` |
| Email enviado ao criar chamado | `chamados/signals.py` (post_save) |
| Inventário: histórico detalhado captura 16 campos | `inventario/views.py:inventario_edit` |
| Inventário: responsável filtrado por setor | `inventario/forms.py` + JS |
| Tarefas: responsável só mostra usuários do setor T.I | `tarefas/forms.py` |
| Portal: solicitante é o próprio usuário, setor vem do perfil | `portal/views.py` |
| Portal: imagem anexada vai pra `imagem_solicitante` | `portal/views.py` |
| Perfil criado automaticamente ao criar usuário | `usuarios/models.py` (signal post_save) |
| Sidebar estado colapsado persiste em localStorage | `base.html` + `main.js` |
| Dashboard e portal atualizam via AJAX a cada 15s | Templates (setInterval + fetch) |

---

## 7. ESTRUTURA DE CADA APP

```
app/
├── __init__.py
├── models.py       # Tabelas do banco (ORM Django)
├── views.py        # Lógica de negócio (controllers)
├── urls.py         # Rotas da app
├── forms.py        # Formulários (validação + widgets)
├── admin.py        # Registro no Django Admin
├── apps.py         # Config da app (signals)
├── signals.py      # Sinais (ex: email ao criar chamado) — apenas em chamados/
├── migrations/     # Histórico do banco
│   └── 0001_initial.py  # Migração inicial (estado final)
└── templates/
    └── app/        # Templates HTML da app
```

---

## 8. PERGUNTAS COMUNS DO COORDENADOR

**"O sistema escala?"** → Django + PostgreSQL suportam milhares de usuários. O Gunicorn com 3 workers é adequado para uso interno. Para escalar, aumente workers ou adicione containers.

**"É seguro?"** → CSRF, XSS protection, require_POST, login_required em todas as views, senhas com hash bcrypt. Em produção, HTTPS via Nginx + HSTS.

**"Como faz backup?"** → Backup do PostgreSQL: `pg_dump sistema_ti > backup.sql`. Arquivos de mídia: copiar pasta `media/`.

**"Como adicionar um setor novo?"** → Adicionar em `SETOR_CHOICES` nos 3 models (chamados, inventario, usuarios). Rodar migration.

**"O portal é responsivo?"** → Sim, usa Bootstrap 5.3 com grid responsivo. Funciona em desktop e mobile.
