import logging

from django.db import models
from django.conf import settings
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin
)

log = logging.getLogger(__name__)
# >>> MANAGERS <<< #

class TrackTrainsUserManager(BaseUserManager):
    """
    Redefined user manager for track trains application
    Registration only by invite
    """

    def create_user(self, email, inviter, password=None):
        """
        Only thing we are looking for is email,
        but user can be registered only through invitation.
        """

        if not email:
            msg = "Email is mandatory param for user creation"
            log.warning(msg)
            raise ValueError(msg)

        if not inviter:
            msg = "Inviter is mandatory param for user creation"
            log.warning(msg)
            raise ValueError(msg)

        invites4newuser = 0
        if inviter.invites_counter > 0:
            inviter.invites_counter -= 1
            invites4newuser = inviter.invites_counter
            inviter.save()
        elif inviter.is_superuser:
            invites4newuser = 3
        else:
            msg = "Inviter has no invitations"
            log.warning(msg)
            raise ValueError(msg)

        user = self.model(
            email=TrackTrainsUserManager.normalize_email(email),
            inviter=inviter,
            invites_counter=invites4newuser
        )

        user.set_password(password)
        user.save(using=self._db)
        log.info("User %s has been created." % user.email)
        return user

    def create_superuser(self, email, password):
        """
        Creates a superuser with given email and password
        the invites_counter is 0
        because superuser has unlimited number of invites
        """
        # TODO this method almost the same as create_user,
        #       consider the way to use create_user inside
        if not email:
            msg = "Email is mandatory param for user creation"
            log.warning(msg)
            raise ValueError(msg)

        user = self.model(
            email=TrackTrainsUserManager.normalize_email(email),
            inviter=None,
            invites_counter=0
        )

        user.set_password(password)

        user.is_superuser = True
        user.is_staff = True

        user.save(using=self._db)
        log.warning("SuperUser %s has been created.")
        return user

# >>> MODELS <<< #
class TrackTrainsUser(AbstractBaseUser, PermissionsMixin):
    """
    Redefined user model
    """
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
        db_index=True
    )

    inviter = models.ForeignKey(
        'self',
        related_name = "The person who invited this user",
        null=True,
        blank=True
    )

    invites_counter = models.PositiveSmallIntegerField(
        verbose_name="The number of remaining invitations",
        default=0
    )

    USERNAME_FIELD = USERNAME_FIELD
    REQUIRED_FIELDS = REQUIRED_FIELDS

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    reset_hash = models.CharField(
        max_length=255,
        null=False,
        blank=True
    )

    objects = TrackTrainsUserManager()

    def get_full_name(self):
        if self.inviter:
            return "%s invited by %s" % (self.email, self.inviter.email)
        else:
            return "%s the superuser" % (self.email)

    def get_short_name(self):
        return self.email

    def __unicode__(self):
        return self.get_short_name()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
