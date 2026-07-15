from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from chamados.models import Chamado
from inventario.models import Equipamento
from tarefas.models import Tarefa
from conhecimento.models import Categoria, Artigo
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados iniciais para demonstracao'

    def handle(self, *args, **options):
        self.stdout.write('Criando dados iniciais...')

        if not settings.DEBUG:
            self.stdout.write(self.style.WARNING('AVISO: Executando seed em producao. Use apenas para desenvolvimento.'))
            return

        admin_pass = 'admin123'
        user_pass = '123456'

        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@abmti.com.br', admin_pass)
            self.stdout.write(self.style.SUCCESS(f'Superusuario admin criado (admin/{admin_pass})'))

        tecnicos = []
        nomes = [('Joao', 'Silva'), ('Maria', 'Santos'), ('Carlos', 'Oliveira')]
        for first, last in nomes:
            username = first.lower()
            if not User.objects.filter(username=username).exists():
                u = User.objects.create_user(username, f'{username}@abmti.com.br', user_pass,
                    first_name=first, last_name=last)
                tecnicos.append(u)
                self.stdout.write(f'Usuario {username} criado')

        admin = User.objects.get(username='admin')

        # Chamados de exemplo
        chamados_data = [
            {'titulo': 'Computador não liga', 'descricao': 'Usuário relata que o computador desktop Dell não está ligando após queda de energia.', 'solicitante': 'Ana Costa', 'setor': 'Financeiro', 'prioridade': 'alta', 'status': 'aberto'},
            {'titulo': 'Sem acesso ao e-mail', 'descricao': 'Colaborador não consegue acessar o e-mail corporativo desde a manhã de hoje.', 'solicitante': 'Pedro Alves', 'setor': 'RH', 'prioridade': 'media', 'status': 'aberto'},
            {'titulo': 'Impressora HP não imprime', 'descricao': 'Impressora HP LaserJet do 3º andar não está imprimindo, exibe luz laranja piscando.', 'solicitante': 'Marina Lima', 'setor': 'Comercial', 'prioridade': 'media', 'status': 'aberto'},
            {'titulo': 'Internet lenta no setor comercial', 'descricao': 'Toda a equipe do setor comercial está com a internet extremamente lenta hoje.', 'solicitante': 'Roberto Neves', 'setor': 'Comercial', 'prioridade': 'critica', 'status': 'andamento'},
            {'titulo': 'Instalar software de nota fiscal', 'descricao': 'Preciso instalar o emissor de NF-e na máquina nova do financeiro.', 'solicitante': 'Carla Mendes', 'setor': 'Financeiro', 'prioridade': 'baixa', 'status': 'aberto'},
            {'titulo': 'Monitor piscando', 'descricao': 'O monitor Samsung do usuário fica piscando intermitentemente.', 'solicitante': 'Lucas Faria', 'setor': 'TI', 'prioridade': 'baixa', 'status': 'resolvido'},
            {'titulo': 'Atualizar antivírus', 'descricao': 'Realizar atualização do antivírus em todas as máquinas do escritório.', 'solicitante': 'TI', 'setor': 'TI', 'prioridade': 'alta', 'status': 'andamento'},
        ]

        for i, cd in enumerate(chamados_data):
            if not Chamado.objects.filter(titulo=cd['titulo']).exists():
                Chamado.objects.create(
                    titulo=cd['titulo'],
                    descricao=cd['descricao'],
                    solicitante=cd['solicitante'],
                    setor=cd['setor'],
                    prioridade=cd['prioridade'],
                    status=cd['status'],
                    tecnico=tecnicos[i % len(tecnicos)] if tecnicos else None,
                    criado_por=admin,
                    criado_em=date.today() - timedelta(days=i),
                )
                self.stdout.write(f'Chamado "{cd["titulo"]}" criado')

        # Equipamentos
        equipamentos_data = [
            {'patrimonio': 'PAT-001', 'categoria': 'computador', 'marca': 'Dell', 'modelo': 'Optiplex 7090', 'setor': 'ti', 'responsavel': 'João Silva', 'status': 'ativo', 'hostname': 'SRV-ADM-01', 'numero_serie': 'SN789012', 'ip': '192.168.1.10'},
            {'patrimonio': 'PAT-002', 'categoria': 'notebook', 'marca': 'Lenovo', 'modelo': 'ThinkPad X1', 'setor': 'rh', 'responsavel': 'Ana Costa', 'status': 'ativo', 'hostname': 'NB-FIN-01', 'numero_serie': 'SN123456', 'ip': '192.168.1.20'},
            {'patrimonio': 'PAT-003', 'categoria': 'impressora', 'marca': 'HP', 'modelo': 'LaserJet M404', 'setor': 'atendimento', 'responsavel': '', 'status': 'manutencao', 'numero_serie': 'SN654321'},
            {'patrimonio': 'PAT-004', 'categoria': 'switch', 'marca': 'Cisco', 'modelo': 'Catalyst 2960', 'setor': 'ti', 'responsavel': 'João Silva', 'status': 'ativo', 'numero_serie': 'SN987654', 'ip': '192.168.1.1'},
        ]

        for ed in equipamentos_data:
            if not Equipamento.objects.filter(patrimonio=ed['patrimonio']).exists():
                Equipamento.objects.create(**ed)
                self.stdout.write(f'Equipamento {ed["patrimonio"]} criado')

        # Tarefas
        tarefas_data = [
            {'titulo': 'Backup mensal dos servidores', 'prioridade': 'alta', 'status': 'a_fazer', 'prazo': date.today() + timedelta(days=5)},
            {'titulo': 'Atualizar inventário de software', 'prioridade': 'media', 'status': 'andamento', 'prazo': date.today() + timedelta(days=3)},
            {'titulo': 'Trocar fonte do PAT-001', 'prioridade': 'alta', 'status': 'a_fazer', 'prazo': date.today() + timedelta(days=2)},
            {'titulo': 'Revisar políticas de segurança', 'prioridade': 'media', 'status': 'concluido', 'prazo': date.today() - timedelta(days=2)},
            {'titulo': 'Configurar novo switch', 'prioridade': 'critica', 'status': 'a_fazer', 'prazo': date.today() + timedelta(days=1)},
        ]

        for td in tarefas_data:
            if not Tarefa.objects.filter(titulo=td['titulo']).exists():
                Tarefa.objects.create(
                    titulo=td['titulo'],
                    prioridade=td['prioridade'],
                    status=td['status'],
                    prazo=td['prazo'],
                    responsavel=tecnicos[0] if tecnicos else admin,
                )
                self.stdout.write(f'Tarefa "{td["titulo"]}" criada')

        # Base de Conhecimento
        if not Categoria.objects.filter(nome='Redes').exists():
            Categoria.objects.create(nome='Redes', descricao='Artigos sobre configuração de rede')
            Categoria.objects.create(nome='Hardware', descricao='Manuais e guias de hardware')
            Categoria.objects.create(nome='Software', descricao='Tutoriais de instalação e configuração de software')

        artigos_data = [
            {'titulo': 'Como configurar VPN corporativa', 'conteudo': 'Guia passo a passo para configurar a VPN...\n\n1. Baixe o cliente VPN\n2. Instale seguindo o assistente\n3. Configure com o endereço vpn.empresa.com.br\n4. Faça login com suas credenciais', 'categoria': 'Redes'},
            {'titulo': 'Troubleshooting de impressoras HP', 'conteudo': 'Problemas comuns e soluções...\n\n- Luz laranja piscando: toner baixo\n- Papel atolado: abrir tampa traseira\n- Não imprime: verificar fila de impressão', 'categoria': 'Hardware'},
        ]

        for ad in artigos_data:
            if not Artigo.objects.filter(titulo=ad['titulo']).exists():
                Artigo.objects.create(
                    titulo=ad['titulo'],
                    conteudo=ad['conteudo'],
                    categoria=Categoria.objects.filter(nome=ad['categoria']).first(),
                    autor=admin,
                )
                self.stdout.write(f'Artigo "{ad["titulo"]}" criado')

        self.stdout.write(self.style.SUCCESS('\nDados iniciais criados com sucesso!'))
