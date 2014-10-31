import logging

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template import loader, Context

from watcher.models import ByRwTask


log = logging.getLogger(__name__)

def send_invitation_email(from_addr, to_addr, signed_invitation):
    """
        Send the invitation to join
    """
    subject = "Invitation by %s to %s" % (from_addr, settings.HOST)

    text_content = loader.get_template('emails/profiles/invite.txt')
    html_content = loader.get_template('emails/profiles/invite.html')

    log.debug('The hash is: %s', signed_invitation)
    payload = {
        'link_to_signup': 'http://%s/%s/%s/' %
            (settings.HOST, settings.SIGNUP_PAGE, signed_invitation)
    }
    c = Context(payload)

    msg = EmailMultiAlternatives(subject, text_content.render(c), from_addr, [to_addr])
    msg.attach_alternative(html_content.render(c), "text/html")
    msg.send()

    log.debug('The invitation email from %s to %s has been sent' % (from_addr, to_addr))

def send_byrw_notification_email(found, task):
    """
        Notify the task owner that required seat has been found.
        @param found if true then user will be notified that seat has been found
                     if false then user will be notified that seat has been bought
        @param task instance of the ByRwTask model
    """
    action = found and "found" or "bought"
    sign = found and "+" or "-"

    if len(task.train):
        subject = "[Task %d](%s) The seat on train %s has been %s"\
            % (task.id, sign, task.train, action)
    else:
        subject = "[Task %d](%s) The seat has been %s" % (task.id, sign, action)

    text_content = loader.get_template('emails/watcher/notification.txt')
    html_content = loader.get_template('emails/watcher/notification.html')

    cars = dict(ByRwTask.CAR_CHOISES)
    seats = dict(ByRwTask.SEAT_CHOISES)

    data = {
        "departure_date": task.departure_date,
        "departure_point": task.departure_point,
        "destination_point": task.destination_point,
        "train": len(task.train) and task.train or "Any train",
        "car": cars[task.car],
        "seat": seats[task.seat],
        "action": action
    }

    c = Context(data)

    msg = EmailMultiAlternatives(
        subject,
        text_content.render(c),
        "robot@tracktrains.io",
        [task.owner.email])

    msg.attach_alternative(html_content.render(c), "text/html")
    msg.send()
