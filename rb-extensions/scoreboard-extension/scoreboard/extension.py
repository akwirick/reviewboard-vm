# scoreboard Extension for Review Board.

from __future__ import unicode_literals
from datetime import timedelta, datetime

from django.utils.translation import ugettext_lazy as _
from django.conf.urls import patterns, include, url
from django.contrib.auth.models import User
from djblets.datagrid.grids import DataGrid, Column, DateTimeSinceColumn
from djblets.extensions.hooks import URLHook, TemplateHook
from djblets.util.templatetags.djblets_utils import ageid
from reviewboard.accounts.decorators import check_login_required
from reviewboard.extensions.base import Extension
from reviewboard.extensions.hooks import NavigationBarHook
from reviewboard.reviews.models import Review
from reviewboard.site.urlresolvers import local_site_reverse
from scoreboard.models import Scoreboard as Score


class Scoreboard(Extension):
    """Extends Review Board to display a user scoreboard

    Scores are based off of reviewing other people's work.
    """
    metadata = {
        'Name': 'scoreboard',
        'Summary': 'Describe your extension here.',
    }

    def initialize(self):
        NavigationBarHook(
            self,
            entries=[
                {
                    'label': 'Scoreboard',
                    'url_name': 'scoreboard',
                }
            ]
        )
        # Setup the url hooks for creating the links
        URLHook(
            self,
            patterns('', url(r'^scoreboard/$', scoreboard_view, name="scoreboard"))
        )

class ScoreboardDataGrid(DataGrid):
    """
    A datagrid showing a list of review statistics.
    """
    user = Column(_("Username"), link=True, sortable=True)
    fullname = Column(_("Full Name"), field_name="get_full_name",
                      link=True, expand=True)
    timestamp = DateTimeSinceColumn(_("Last Reviewed"),
                                    detailed_label=_("Last Reviewed (Relative)"), shrink=True, link=True,
                                    css_class=lambda r: ageid(r.timestamp))
    month_count = Column(_("Past Month"), link=True, sortable=True)
    weeks_count = Column(_("Past 2 Weeks"), link=True, sortable=True)

    def __init__(self, request,
                 queryset=User.objects.filter(review_groups__name__iexact="engineering").exclude(last_name=None),
                 title=_("Scoreboard")):
        for user in queryset:
            delta = timedelta(days=-62)
            two_months = Review.objects.filter(base_reply_to=None).filter(user=user).filter(
                timestamp__gt=datetime.now() + delta).count()

            if two_months == 0:
                try:
                    inactive = Score.objects.get(user=user)
                    inactive.delete()
                except:
                    continue

            try:
                s = Score.objects.get(user=user)
            except:
                s = Score()
                s.user = user

            s.timestamp = Review.objects.filter(base_reply_to=None).filter(user=user).filter(
                timestamp__gt=datetime.now() + timedelta(days=-62)).latest('timestamp').timestamp
            s.month_count = Review.objects.filter(base_reply_to=None).filter(user=user).filter(
                timestamp__gt=datetime.now() + timedelta(days=-30)).count()
            s.weeks_count = Review.objects.filter(base_reply_to=None).filter(user=user).filter(
                timestamp__gt=datetime.now() + timedelta(days=-14)).count()
            s.save()

        scoresquery = Score.objects.all()
        DataGrid.__init__(self, request, scoresquery, title)
        self.default_sort = ["-month_count", "-weeks_count"]
        self.default_columns = [
            "fullname", "month_count", "weeks_count", "timestamp",
        ]

    # @staticmethod
    def link_to_object(self, obj, value):
        return local_site_reverse("user", args=[obj.username])

@check_login_required
def scoreboard_view(request, template_name='datagrids/datagrid.html'):
    grid = ScoreboardDataGrid(request)
    return grid.render_to_response(template_name)