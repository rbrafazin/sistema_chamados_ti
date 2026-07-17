# ABM TI — Sistema de Chamados

Sistema web para gestão de TI desenvolvido com **Django 4.2 + PostgreSQL + Docker**.

---

## Módulos (9 apps)

| Módulo | Descrição |
|---|---|
| **Dashboard** | Visão geral com cards de stats, chamados recentes, tarefas pendentes e auto-refresh (15s) |
| **Chamados** | CRUD com filtros, histórico, imagens separadas (solicitante/técnico), dropdown de setor e solicitante |
| **Inventário** | Controle de equipamentos com categorias, specs técnicas, filtro de campos por tipo, histórico detalhado |
| **Portal** | Tela limpa para funcionários abrirem chamados com imagem, ver status e resposta do técnico |
| **Base de Conhecimento** | Artigos com categorias, autor e contador de visualizações |
| **Tarefas** | Quadro Kanban (A Fazer / Em Andamento / Concluído) com prioridades, prazos e responsáveis |
| **Calendário** | FullCalendar com eventos, navegação por mês/ano e sidebar de próximos eventos |
| **Relatórios** | Gráficos com Chart.js, stats mensais, exportação CSV (Excel) e PDF por email |
| **Usuários** | Gestão de usuários com perfis, setor (14 opções), filtro e controle de acesso via `is_staff` |

---

## Tecnologias

| Camada | Tecnologia |
|---|---|
| **Backend** | Python 3.11 + Django 4.2 |
| **Banco de Dados** | PostgreSQL 15 |
| **Frontend** | Bootstrap 5.3 + Chart.js + FullCalendar 5 |
| **Containerização** | Docker + Docker Compose (dev: runserver, prod: Gunicorn + Nginx) |
| **Relatórios** | WeasyPrint (PDF) + QuickChart (gráficos) |
| **Fontes** | Inter (Google Fonts) |

---

## Pré-requisitos

- **Docker Desktop** instalado
- Portas 8000 (dev) ou 80 (prod) disponíveis

---

## Instalação — Desenvolvimento

```bash
git clone https://github.com/rbrafazin/sistema_chamados_ti.git
cd sistema_chamados_ti
docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

Acesse: **http://localhost:8000**

---

## Instalação — Produção

1. Copie `.env` para `.env.prod` e edite com valores reais (DEBUG=False, senhas fortes, domínio)
2. Suba com o compose de produção:

```bash
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

3. Acesse pelo IP ou domínio na porta 80

---

## Controle de Acesso

| Tipo | Campo | Acesso |
|---|---|---|
| **Técnico (TI)** | `is_staff=True` | Sistema completo (8 módulos) |
| **Funcionário** | `is_staff=False` | Portal (abrir chamados e ver status) |

O middleware `StaffRequiredMiddleware` redireciona automaticamente usuários sem `is_staff` para o portal.

---

## Variáveis de Ambiente (`.env`)

```env
DEBUG=False
SECRET_KEY=<chave-aleatoria-longa>
DB_NAME=sistema_ti
DB_USER=admin
DB_PASSWORD=<senha-forte>
DB_HOST=db
DB_PORT=5432
ALLOWED_HOSTS=seu-dominio.com,ip-do-servidor
SITE_URL=http://seu-dominio.com

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=<senha-app-gmail>
NOTIFICACAO_EMAIL=ti@empresa.com.br
RELATORIO_EMAIL=relatorios@abmti.com.br
```

> Use senha de app do Gmail em https://myaccount.google.com/apppasswords

---

## Estrutura do Projeto

```
sistema_chamados_ti/
├── core/                       # Configuração central
│   ├── settings.py             # Django settings + Bootstrap 5 dark overrides
│   ├── urls.py                 # Roteador principal (9 apps + login)
│   ├── middleware.py           # StaffRequiredMiddleware
│   ├── context_processors.py   # Contador de chamados abertos (sidebar)
│   ├── views.py                # CustomLoginView (staff → sistema, não-staff → portal)
│   ├── utils.py                # Função compartilhada usuarios_por_setor_json
│   └── templates/              # base.html, login.html, pagination.html
├── dashboard/                  # Dashboard + comando seed_data de demonstração
├── chamados/                   # Chamados (CRUD, filtros, signals de email, histórico)
├── inventario/                 # Inventário (CRUD, campos dinâmicos por categoria, histórico)
├── portal/                     # Portal do funcionário (abrir chamados, ver status)
├── conhecimento/               # Base de Conhecimento (artigos, categorias)
├── tarefas/                    # Tarefas (Kanban, responsável T.I, prioridades)
├── calendario/                 # Calendário (FullCalendar, navegação mês/ano)
├── relatorios/                 # Relatórios (Chart.js, CSV, PDF por email)
├── usuarios/                   # Usuários (CRUD, perfil, setor, filtro)
├── static/
│   ├── css/style.css           # Design system (Linear · GitHub Dark · Vercel)
│   ├── js/main.js              # Sidebar colapsável + alertas
│   └── img/                    # Logo ABM
├── media/                      # Uploads (imagens de chamados/equipamentos)
├── logs/                       # Logs da aplicação
├── Dockerfile
├── docker-compose.yml          # Desenvolvimento (runserver)
├── docker-compose.prod.yml     # Produção (Gunicorn + Nginx)
├── nginx.conf                  # Proxy reverso com gzip + cache de estáticos
├── requirements.txt
├── .env                        # Variáveis de ambiente (dev)
├── .gitignore
├── manage.py
├── DOCUMENTACAO.md             # Documentação técnica completa
├── DIAGRAMA.md                 # Diagramas UML (Mermaid)
└── README.md
```

---

## Funcionalidades

- **Auto-refresh** — Dashboard e portal atualizam via AJAX a cada 15s
- **Sidebar colapsável** — Estado persiste em localStorage entre páginas
- **Campos dinâmicos** — Formulário de inventário esconde campos irrelevantes por categoria
- **Filtro em cascata** — Setor selecionado filtra solicitante/responsável dinamicamente
- **Histórico detalhado** — Inventário registra exatamente quais campos foram alterados
- **Paginação numerada** — `‹ 1 2 3 ›` em todas as listagens
- **CSV para Excel** — Delimitador `;` + BOM UTF-8, abre direto no Excel sem acentos quebrados
- **Badges coloridos** — Verde, azul, laranja, vermelho e cinza padronizados
- **Migrations limpas** — 1 `0001_initial.py` por app (sem histórico de alterações no banco)

---

## Melhores Práticas Implementadas

- Estrutura modular com 9 apps Django
- `select_related` em todas as queries com FK
- Variáveis de ambiente com `python-decouple` + `.env`
- Healthcheck no PostgreSQL e Django
- Proteção CSRF em todos os formulários
- XSS protection com escape HTML no JavaScript
- Headers de segurança em produção (HSTS, SSL, cookies seguros)
- Logging configurado (console + arquivo)
- Persistência de dados com Docker Volumes
- Seed data protegido (não executa em produção)
