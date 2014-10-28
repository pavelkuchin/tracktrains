import logging

from django.utils import timezone
from django.core.management.base import BaseCommand

from watcher.models import ByRwTask
from utils.gateways import GatewayByRw
from utils.email import send_byrw_notification_email


class Command(BaseCommand):
    help = """
    The job for processing by rw tasks,
    the result will be sent to task owner through email
    """

    log = logging.getLogger(__name__)

    def __looking4seat(self, details, car, seat):
        """
        Looking for seat for specific car type or any car type
        """
        result = False

        self.log.info("Looking for seat: %s" % seat)
        self.log.debug("%s" % unicode(details))
        if car != "ANY":
            if seat in details[car] and details[car][seat]:
                self.log.info("Seat has been found")
                result = True
        else:
            for k,v in details.items():
                if seat in v and v[seat]:
                    self.log.info("Seat has been found")
                    result = True
                    break
        return result

    def handle(self, *args, **options):
        self.log.info('Processing...')

        tasks = ByRwTask.objects.filter(is_active=True).order_by(
            'departure_point',
            'destination_point',
            'departure_date')

        departure = None
        destination = None
        date = None

        with GatewayByRw() as gw:
            for i in tasks:
                trains = None
                found_train = False
                found_car = False
                found_seat = False

                self.log.info("The task: %s" % unicode(i))

                now = timezone.now()
                i.tracked = now
                if i.departure_date < now.date():
                    self.log.info("The task %s expired" % unicode(i))
                    i.delete()
                    continue

                if (departure != i.departure_point or
                    destination != i.destination_point or
                    date != i.departure_date):

                    departure = i.departure_point
                    destination = i.destination_point
                    date = i.departure_date

                    self.log.info("Getting trains on %s: %s->%s" %
                        (date, unicode(departure), unicode(destination)))
                    trains = gw.get_trains(departure, destination, date)

                # If any train will be fine
                if len(i.train) == 0 and len(trains):
                    self.log.info("Any train will be fine")
                    found_train = True
                else:
                    self.log.info("Looking for train: %s" % i.train)
                    if i.train in trains.keys():
                        self.log.info("Train has been found")
                        found_train = True

                # Looking for car
                if i.car == 'ANY':
                    self.log.info("Any car will be fine")
                    found_car = True
                else:
                    if found_train:
                        self.log.info("Looking for car type: %s" % i.car)
                        if len(i.train):
                            if i.car in trains[i.train]['types']:
                                self.log.info("The car has been found")
                                found_car = True
                        else:
                            for k,j in trains.items():
                                if i.car in j['types']:
                                    self.log.info("The car has been found")
                                    found_car = True
                                    break

                # Looking for seat
                if i.seat == 'ANY':
                    self.log.info("Any seat will be fine")
                    found_seat = True
                else:
                    if found_train and found_car:
                        if len(i.train):
                            t = trains[i.train]
                            details = gw.get_train_details(
                                t['train_id'],
                                t['types']
                            )
                            found_seat = self.__looking4seat(details, i.car, i.seat)
                        else:
                            for k,j in trains.items():
                                details = gw.get_train_details(
                                    j['train_id'],
                                    j['types']
                                )
                                found_seat = self.__looking4seat(details, i.car, i.seat)


                if found_train and found_car and found_seat:
                    i.is_successful = True
                    send_byrw_notification_email(True, i)
                    self.log.info('Required train has been found')
                else:
                    if i.is_successful:
                        send_byrw_notification_email(False, i)
                    i.is_successful = False

                i.save()
