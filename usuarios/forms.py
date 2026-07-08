from django import forms
from django.contrib.auth.models import User
from .models import Perfil

class PerfilForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, label='Nome', required=False)
    last_name = forms.CharField(max_length=150, label='Sobrenome', required=False)
    email = forms.EmailField(required=False, label='E-mail')

    class Meta:
        model = Perfil
        fields = ['cargo', 'telefone', 'setor']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.usuario:
            self.fields['first_name'].initial = self.instance.usuario.first_name
            self.fields['last_name'].initial = self.instance.usuario.last_name
            self.fields['email'].initial = self.instance.usuario.email
        for field in self.fields.values():
            css = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{css} {existing}'.strip()

    def save(self, commit=True):
        perfil = super().save(commit=False)
        if commit:
            user = perfil.usuario
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.save()
            perfil.save()
        return perfil


class UsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label='Senha', required=False)
    cargo = forms.ChoiceField(choices=Perfil.CARGO_CHOICES, label='Cargo')
    telefone = forms.CharField(max_length=20, required=False, label='Ramal')
    setor = forms.CharField(max_length=100, initial='TI', label='Setor')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            elif isinstance(field.widget, forms.Select):
                css = 'form-select'
                existing = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f'{css} {existing}'.strip()
            else:
                css = 'form-control'
                existing = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f'{css} {existing}'.strip()
        self.fields['username'].help_text = ''
        if self.instance and self.instance.pk:
            self.fields['password'].required = False
        else:
            self.fields['password'].required = True
        if self.instance and hasattr(self.instance, 'perfil'):
            self.fields['cargo'].initial = self.instance.perfil.cargo
            self.fields['telefone'].initial = self.instance.perfil.telefone
            self.fields['setor'].initial = self.instance.perfil.setor

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
            if hasattr(user, 'perfil'):
                perfil = user.perfil
                perfil.cargo = self.cleaned_data.get('cargo', 'tecnico')
                perfil.telefone = self.cleaned_data.get('telefone', '')
                perfil.setor = self.cleaned_data.get('setor', 'TI')
                perfil.save()
        return user
