from django.contrib.auth.models import User
from django.db import models
from reviewboard.reviews.managers import ReviewManager
from django.utils.translation import ugettext_lazy as _

class Scoreboard(models.Model):
    """
    A scoreboard entry.
    """
    user = models.ForeignKey(User, verbose_name=_("user"),
                             related_name="scoreboards")
    timestamp = models.DateTimeField(_('timestamp'))
    month_count = models.IntegerField(_('month_count'))
    weeks_count = models.IntegerField(_('week_count'))

    # Set this up with a ReviewManager to help prevent race conditions and
    # to fix duplicate reviews.
    objects = ReviewManager()

    def __unicode__(self):
        return u"Scoreboard entry of '%s'. Latest Review: '%s'." % (self.user, self.timestamp)

    def get_full_name(self):
        return self.user.get_full_name()

    class Meta:
        ordering = ['timestamp']
        get_latest_by = 'timestamp'