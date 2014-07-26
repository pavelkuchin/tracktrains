import logging

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template import loader
from django.template import RequestContext

log = logging.getLogger(__name__)


def send_invitation_email(request, from_addr, to_addr, signed_invitation):
    subject = "Invitation by %s to %s" % (from_addr, settings.HOST)

    text_content = loader.get_template('emails/profiles/invite.txt')
    html_content = loader.get_template('emails/profiles/invite.html')

    log.debug('The hash is: %s', signed_invitation)
    payload = {
        'link_to_signup': 'http://%s/%s/%s/' %  (settings.HOST, settings.SIGNUP_PAGE, signed_invitation)
    }
    c = RequestContext(request, payload)

    msg = EmailMultiAlternatives(subject, text_content.render(c), from_addr, [to_addr])
    msg.attach_alternative(html_content.render(c), "text/html")
    msg.send()

    log.debug('The invitation email from %s to %s has been sent' % (from_addr, to_addr))
