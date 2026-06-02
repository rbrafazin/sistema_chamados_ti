from django import template

register = template.Library()

ICONES = {
    'computador': 'bi-pc-display',
    'notebook': 'bi-laptop',
    'impressora': 'bi-printer',
    'monitor': 'bi-display',
    'roteador': 'bi-wifi',
    'switch': 'bi-hdd-network',
    'outro': 'bi-device-hdd',
}


@register.filter
def icone_categoria(valor):
    return ICONES.get(valor, 'bi-device-hdd')
