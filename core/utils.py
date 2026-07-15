from django.contrib.auth.models import User
import json


def usuarios_por_setor_json():
    dados = {}
    for u in User.objects.select_related('perfil').filter(perfil__setor__isnull=False):
        s = u.perfil.setor
        if s not in dados:
            dados[s] = []
        dados[s].append({
            'id': u.id,
            'value': u.get_full_name() or u.username,
            'name': u.get_full_name() or u.username,
        })
    return json.dumps(dados)
