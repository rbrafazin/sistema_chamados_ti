# 📐 Diagrama UML — ABM TI

> Para visualizar: abra este arquivo no [GitHub](https://github.com/rbrafazin/sistema_chamados_ti) ou cole o código em [mermaid.live](https://mermaid.live)

---

## 1. Diagrama de Classes

```mermaid
classDiagram
    direction TB

    class User {
        +id: int
        +username: string
        +first_name: string
        +last_name: string
        +email: string
        +is_staff: bool
        +is_active: bool
        +password: string
    }

    class Perfil {
        +id: int
        +setor: string
        +telefone: string
        +avatar: string
    }

    class Chamado {
        +id: int
        +titulo: string
        +descricao: text
        +solicitante: string
        +setor: string
        +categoria: string
        +prioridade: string
        +status: string
        +observacoes: text
        +imagem_tecnica: string
        +imagem_solicitante: string
        +criado_em: datetime
        +atualizado_em: datetime
    }

    class HistoricoChamado {
        +id: int
        +acao: string
        +descricao: text
        +criado_em: datetime
    }

    class Equipamento {
        +id: int
        +patrimonio: string
        +hostname: string
        +categoria: string
        +marca: string
        +modelo: string
        +numero_serie: string
        +processador: string
        +memoria_ram: string
        +armazenamento: string
        +sistema_operacional: string
        +ip: string
        +mac_address: string
        +setor: string
        +status: string
        +observacoes: text
        +imagem: string
        +criado_em: datetime
        +atualizado_em: datetime
    }

    class HistoricoEquipamento {
        +id: int
        +acao: string
        +descricao: text
        +criado_em: datetime
    }

    class Tarefa {
        +id: int
        +titulo: string
        +descricao: text
        +prioridade: string
        +status: string
        +prazo: date
        +criado_em: datetime
        +atualizado_em: datetime
    }

    class Categoria {
        +id: int
        +nome: string
        +descricao: text
        +criado_em: datetime
    }

    class Artigo {
        +id: int
        +titulo: string
        +conteudo: text
        +anexo: string
        +visualizacoes: int
        +criado_em: datetime
        +atualizado_em: datetime
    }

    class Evento {
        +id: int
        +titulo: string
        +descricao: text
        +tipo: string
        +cor: string
        +data_inicio: datetime
        +data_fim: datetime
        +dia_todo: bool
        +criado_em: datetime
    }

    User "1" -- "0..1" Perfil : usuario
    User "1" -- "0..*" Chamado : criado_por
    User "1" -- "0..*" Chamado : tecnico
    User "1" -- "0..*" HistoricoChamado : usuario
    Chamado "1" -- "0..*" HistoricoChamado : chamado

    User "1" -- "0..*" Equipamento : responsavel
    User "1" -- "0..*" HistoricoEquipamento : usuario
    Equipamento "1" -- "0..*" HistoricoEquipamento : equipamento

    User "1" -- "0..*" Tarefa : responsavel
    User "1" -- "0..*" Tarefa : criado_por

    User "1" -- "0..*" Artigo : autor
    Categoria "1" -- "0..*" Artigo : categoria

    User "1" -- "0..*" Evento : criado_por
```

---

## 2. Diagrama de Acesso (Login → Sistema ou Portal)

```mermaid
flowchart TD
    A[Usuário acessa URL] --> B[GET /accounts/login/]
    B --> C[Formulário de Login]
    C --> D{Credenciais válidas?}
    D -->|Não| C
    D -->|Sim| E{is_staff?}
    E -->|True| F[🔀 Redireciona para /]
    E -->|False| G[🔀 Redireciona para /portal/]
    F --> H[Dashboard do Sistema]
    G --> I[Portal de Chamados]
    H --> J{Usuário acessa URL do sistema?}
    J -->|Sim| K[StaffRequiredMiddleware]
    K --> L{Permitido?}
    L -->|staff| H
    L -->|não-staff| I
```

---

## 3. Diagrama de Sequência — Criar Chamado

```mermaid
sequenceDiagram
    actor TI as 👤 Técnico (TI)
    participant View as chamados/views.py
    participant Form as chamados/forms.py
    participant Model as chamados/models.py
    participant DB as PostgreSQL
    participant Signal as chamados/signals.py
    participant Email as Servidor SMTP

    TI->>View: GET /chamados/novo/
    View->>Form: ChamadoForm() vazio
    View-->>TI: renderiza form.html

    TI->>View: POST /chamados/novo/ (dados + imagem)
    View->>Form: ChamadoForm(POST, FILES)
    View->>Form: form.is_valid()
    Form-->>View: ✅ válido

    View->>Model: form.save(commit=False)
    View->>Model: chamado.criado_por = request.user
    View->>Model: chamado.save()
    Model->>DB: INSERT INTO chamados_chamado

    View->>Model: HistoricoChamado.objects.create()
    Model->>DB: INSERT INTO chamados_historicochamado

    DB-->>Signal: post_save disparado (created=True)
    Signal->>Email: send_mail() — notificação de novo chamado
    Signal-->>Signal: logger.exception() se falhar

    View-->>TI: redirect para lista de chamados
```

---

## 4. Diagrama de Sequência — Auto-Refresh (Dashboard)

```mermaid
sequenceDiagram
    participant Browser as Navegador
    participant View as dashboard/views.py
    participant DB as PostgreSQL

    loop a cada 15 segundos
        Browser->>View: GET /stats/ (AJAX fetch)
        View->>DB: Chamado.objects.filter(status='aberto').count()
        View->>DB: Chamado.objects.filter(prioridade='critica').count()
        View->>DB: Equipamento.objects.filter(status='ativo').count()
        View->>DB: Evento.objects.filter(data_inicio__date=today).count()
        View->>DB: Chamado.objects.order_by('-criado_em')[:10]
        View-->>Browser: JSON { chamados_abertos, chamados_criticos, ... }
        Browser->>Browser: Atualiza números nos cards + tabela
    end
```

---

## 5. Diagrama de Sequência — Filtro Dinâmico (Solicitante por Setor)

```mermaid
sequenceDiagram
    actor TI as 👤 Técnico
    participant HTML as form.html
    participant JS as JavaScript (inline)
    participant DOM as Navegador

    Note over HTML: usuarios_json = {ti: [...], rh: [...], ...}

    TI->>DOM: Seleciona Setor = "T.I"
    DOM->>JS: evento 'change' no select[name="setor"]
    JS->>JS: _filtrar() — pega usuarios_json['ti']
    JS->>DOM: innerHTML = <option>João Silva</option><option>Maria Santos</option>
    DOM-->>TI: Dropdown de Solicitante populado com nomes do T.I

    TI->>DOM: Seleciona "João Silva" e submete
    DOM->>HTML: POST com solicitante="João Silva"
    Note over HTML: form.fields['solicitante'].queryset = User.objects.all()
    Note over HTML: ✅ Validação aceita o valor
```

---

## 6. Diagrama de Componentes (Arquitetura Física)

```mermaid
flowchart LR
    subgraph Docker_Dev
        direction TB
        Web_Dev[Django runserver<br/>Porta 8000]
        DB_Dev[(PostgreSQL<br/>Porta 5432)]
        Web_Dev --> DB_Dev
    end

    subgraph Docker_Prod
        direction TB
        Nginx[Nginx<br/>Porta 80]
        Web_Prod[Gunicorn<br/>3 workers]
        DB_Prod[(PostgreSQL<br/>Porta 5432)]
        Nginx --> Web_Prod
        Web_Prod --> DB_Prod
        Static[Arquivos estáticos]
        Media[Uploads /media/]
        Nginx --> Static
        Nginx --> Media
    end

    User[👤 Usuário] --> Docker_Dev
    User2[👤 Usuário] --> Docker_Prod
```

---

## 7. Diagrama de Estados — Status do Chamado

```mermaid
stateDiagram-v2
    [*] --> Aberto : Chamado criado
    Aberto --> Em_Andamento : Técnico inicia
    Em_Andamento --> Resolvido : Técnico resolve
    Resolvido --> [*] : Finalizado (travado)
    note right of Resolvido : Não pode ser editado
    note right of Resolvido : Não pode mudar status
```

---

**Como visualizar estes diagramas:**
1. Abra este arquivo `.md` no GitHub — renderiza automaticamente
2. Ou cole o código em https://mermaid.live
3. Ou instale o plugin "Markdown Preview Mermaid" no VS Code
