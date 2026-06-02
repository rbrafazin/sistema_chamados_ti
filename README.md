# ABM TI — Sistema de Chamados

Sistema web para gerenciamento de TI desenvolvido com Django + PostgreSQL + Docker.

## Módulos

| Módulo | Descrição |
|---|---|
| **Dashboard** | Visão geral com indicadores clicáveis, chamados recentes e tarefas pendentes |
| **Chamados** | CRUD completo com filtros, pesquisa, histórico de alterações e notificação por e-mail |
| **Inventário** | Controle de equipamentos com ícones por categoria, especificações técnicas e histórico |
| **Base de Conhecimento** | Artigos com categorias, tags e editor de texto |
| **Tarefas** | Quadro Kanban (A Fazer / Em Andamento / Concluído) com prioridades e prazos |
| **Calendário** | Eventos com FullCalendar, prioridade com cor automática e clicar no dia para criar |
| **Relatórios** | Gráficos com Chart.js (status, prioridade, categoria, produtividade mensal) |
| **Usuários** | Gestão de usuários com perfis, cargos, permissões e tema salvo por usuário |

## Tecnologias

- **Backend:** Django 4.2
- **Banco de Dados:** PostgreSQL 15
- **Frontend:** Bootstrap 5, Chart.js, FullCalendar
- **Containerização:** Docker & Docker Compose
- **Servidor Web:** Gunicorn (produção)

## Pré-requisitos

- Docker e Docker Compose instalados
- Portas 8000 e 5432 disponíveis

## Instalação Rápida (desenvolvimento)

```bash
git clone <repo-url> sistema_chamados_ti
cd sistema_chamados_ti

# Build e start
docker compose up --build

# Em outro terminal — migrações (especificar apps na primeira vez)
docker exec django_app python manage.py makemigrations chamados inventario conhecimento tarefas calendario usuarios
docker exec django_app python manage.py migrate

# Criar superusuário
docker exec -it django_app python manage.py createsuperuser

# (Opcional) Popular com dados de demonstração (só funciona com DEBUG=True)
docker exec django_app python manage.py seed_data
```

Acesse: **http://localhost:8000**

## Colocar em Produção

```bash
# 1. Zerar dados de desenvolvimento (mantém admin)
docker exec django_app python manage.py shell -c "
from chamados.models import Chamado, HistoricoChamado
from inventario.models import Equipamento, HistoricoEquipamento
from conhecimento.models import Artigo, Categoria, Tag
from tarefas.models import Tarefa
from calendario.models import Evento
from django.contrib.auth.models import User

HistoricoChamado.objects.all().delete()
Chamado.objects.all().delete()
HistoricoEquipamento.objects.all().delete()
Equipamento.objects.all().delete()
Artigo.objects.all().delete()
Categoria.objects.all().delete()
Tag.objects.all().delete()
Tarefa.objects.all().delete()
Evento.objects.all().delete()
User.objects.exclude(username='admin').delete()
print('Sistema zerado.')
"

# 2. Editar .env com valores reais (senhas fortes, e-mail, ALLOWED_HOSTS)
# 3. Subir com compose de produção
docker compose -f docker-compose.prod.yml up -d --build
docker exec django_app python manage.py migrate
docker exec django_app python manage.py collectstatic --noinput

# 4. Criar técnicos pela interface (menu Usuários)
# 5. Configurar HTTPS com Nginx + Certbot ou Cloudflare
```

## Comandos Úteis (dentro do container)

```bash
docker exec -it django_app bash

# Migrações
python manage.py makemigrations
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Dados de demonstração (apenas com DEBUG=True)
python manage.py seed_data

# Shell Django
python manage.py shell

# Coletar estáticos
python manage.py collectstatic --noinput
```

## Estrutura do Projeto

```
sistema_chamados_ti/
├── core/                       # Configurações Django
│   ├── settings.py
│   ├── urls.py
│   ├── context_processors.py   # Contadores da sidebar
│   └── templates/
│       ├── base.html           # Layout com sidebar + navbar
│       ├── includes/           # Componentes reutilizáveis (paginação)
│       └── registration/
│           └── login.html
├── dashboard/                  # Dashboard + comando seed_data
├── chamados/                   # Chamados (CRUD, filtros, sinais de e-mail)
├── inventario/                 # Inventário (CRUD, ícones, template tags)
├── conhecimento/               # Base de Conhecimento (artigos, categorias, tags)
├── tarefas/                    # Tarefas (Kanban, detalhes)
├── calendario/                 # Calendário (FullCalendar, eventos por prioridade)
├── relatorios/                 # Relatórios (Chart.js, 4 gráficos)
├── usuarios/                   # Usuários (perfis, tema por usuário, permissões)
├── static/
│   ├── css/style.css           # Tema enterprise blue (claro/escuro)
│   ├── js/main.js              # JavaScript global
│   └── img/                    # Logo e imagens
├── Dockerfile
├── docker-compose.yml          # Desenvolvimento (runserver)
├── docker-compose.prod.yml     # Produção (Gunicorn + Nginx)
├── nginx.conf                  # Proxy reverso produção
├── requirements.txt
├── .env                        # Variáveis de ambiente (dev)
├── .env.prod                   # Template para produção
├── .gitignore
├── manage.py
└── README.md
```

## Variáveis de Ambiente (.env)

```env
DEBUG=True
SECRET_KEY=substitua-por-uma-chave-longa-e-aleatoria
DB_NAME=sistema_ti
DB_USER=admin
DB_PASSWORD=substitua-por-senha-forte
DB_HOST=db
DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1

# Email (notificações de chamados)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app
NOTIFICACAO_EMAIL=ti@empresa.com.br
```

> **Importante:** Use uma senha de app do Gmail, não sua senha normal. Gere em: https://myaccount.google.com/apppasswords

## Funcionalidades

- **Tema escuro/claro** salvo por usuário (persiste entre dispositivos)
- **Sidebar colapsável** com estado salvo
- **Cards clicáveis** no dashboard (filtram a página de destino)
- **Paginação** em todas as listas (20 itens/página)
- **Ícones** nas categorias do inventário
- **Tags** nos artigos da base de conhecimento
- **Prioridade → cor automática** nos eventos do calendário
- **Notificação por e-mail** ao criar chamado
- **Histórico** de alterações em chamados e equipamentos
- **Try/except** em todas as operações de exclusão
- **Proteção CSRF** em todos os formulários

## Melhores Práticas Implementadas

- Estrutura modular com 8 apps Django independentes
- `select_related` e `prefetch_related` para otimização de queries
- `F()` expressions para evitar race conditions
- Separação de settings com `python-decouple` + `.env`
- Templates com herança (`base.html`) e includes reutilizáveis
- Forms Django com validação server-side
- Logging de erros em sinais (e-mail)
- Cabeçalhos de segurança em produção (HSTS, SSL, cookies seguros)
- Containerização completa com healthcheck no PostgreSQL
- Persistência de dados com Docker Volumes
- Seed data protegido (não executa em produção)
- Código em português para adequação ao domínio

## Sugestões de Melhorias Futuras

- Notificações em tempo real (Django Channels + WebSocket)
- API REST com Django REST Framework
- Sistema de SLA com alertas de prazo
- Portal simplificado para solicitantes (sem acesso ao sistema completo)
- Exportação de relatórios em PDF/Excel
- Integração com Zabbix/Grafana
- Autenticação via LDAP/Active Directory
