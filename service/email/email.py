from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User

class Email:
    def enviar_email_recuperacao(destinatario=None, codigo=None):
        try:
            if not destinatario:
                return False, 'Informe um email!'

            isEmailExistente = User.objects.filter(email=destinatario).first()
            if not isEmailExistente:
                return False, 'Usuário não encontrado!'

            context = {'token': codigo}
            html_content = render_to_string('email_reset_senha.html', context)

            assunto = 'Código de reset de senha Stock Flow!'
            remetente = settings.DEFAULT_FROM_EMAIL
            destinatarios = [destinatario]

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