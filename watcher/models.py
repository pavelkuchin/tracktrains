from django.db import models


class AbstractTask(models.Model):
    """
        Abstract class with initial and the necessary set of field
        (There can be other types of tasks in the future)
    """
    owner = models.ForeignKey(
        'profiles.TrackTrainsUser',
        null=False,
        blank=False
    )

    is_active = models.BooleanField(
        verbose_name="Active for processing",
        default=True
    )
    is_successful = models.BooleanField(
        default=False,
        verbose_name="Seat has been found"
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    tracked = models.DateTimeField(
        verbose_name="When the Job has processed the task last time",
        null=True,
        blank=True
    )

    class Meta:
        abstract = True

class ByRwTask(AbstractTask):
    """
        Task for the By Rainway related job.
    """

    # Choises for seat
    SEAT_CHOISES = (
        ('ANY', 'Any seat'),
        ('B', 'Bottom place'),
        ('T', 'Top place')
    )

    # Choises for cars
    CAR_CHOISES = (
        ('ANY', 'Any type'),
        ('VIP', 'VIP car'),
        ('SLE', 'Sleeping car'),
        ('COM', 'Compartment car'),
        ('RB', 'Reserved-berths car'),
        ('RS', 'Car with regular seats'),
        ('TC', 'Third-class car')
    )

    departure_point = models.CharField(
        verbose_name="The departure station name",
        blank = False,
        max_length = 255
    )
    destination_point = models.CharField(
        verbose_name="The destination station name",
        blank = False,
        max_length = 255
    )
    departure_date = models.DateField(
        verbose_name="The required departure date"
    )
    train = models.CharField(
        verbose_name="The train short code id",
        blank = False,
        max_length = 5
    )
    car = models.CharField(
        verbose_name="Preferred train car type",
        default='ANY',
        choices=CAR_CHOISES,
        max_length=5
    )
    seat = models.CharField(
        verbose_name="Preferred train seat",
        default='ANY',
        choices=SEAT_CHOISES,
        max_length=5
    )

    def __unicode__(self):
        return "%s %s - %s" % (self.train,
            self.departure_point,
            self.destination_point)

    class Meta:
        verbose_name = "By RW Task"
        verbose_name_plural = "By RW Tasks"