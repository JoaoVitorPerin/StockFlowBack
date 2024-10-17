from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from user.models import Usuario
from django.utils import timezone  # Para manipulação de tempo
from datetime import timedelta  # Para adicionar minutos

class Email:
    def enviar_email_recuperacao(destinatario=None, codigo=None):
        try:
            if not destinatario:
                return False, 'Informe um email!'

            # Verificar se o email existe no banco
            usuario = Usuario.objects.filter(email=destinatario).first()
            if not usuario:
                return False, 'Usuário não encontrado!'

            # Definir o código e a validade
            usuario.codigo_reset = codigo  # Código de recuperação fornecido
            usuario.validade_codigo = timezone.now() + timedelta(minutes=10)  # 10 minutos a partir de agora
            usuario.save()  # Salvar no banco de dados

            # Preparar o conteúdo do email
            context = {'token': codigo}
            html_content = render_to_string('email_reset_senha.html', context)

            assunto = 'Código de reset de senha Stock Flow!'
            remetente = settings.DEFAULT_FROM_EMAIL
            destinatarios = [destinatario]

            # Configurar e enviar o email
            email = EmailMessage(
                assunto,
                html_content,
                remetente,
                destinatarios
            )
            email.content_subtype = "html"
            email.send(fail_silently=False)

            return True, 'Email enviado com sucesso'
        except Exception as e:
            return False, str(e)
