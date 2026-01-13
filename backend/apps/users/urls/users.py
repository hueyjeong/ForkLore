from django.urls import path

from ..views import BookmarksView, ChangePasswordView, MeView, ReadingHistoryView

urlpatterns = [
    path("me/", MeView.as_view(), name="me"),
    path("me/password/", ChangePasswordView.as_view(), name="change_password"),
    path("me/reading-history/", ReadingHistoryView.as_view(), name="me-reading-history"),
    path("me/bookmarks/", BookmarksView.as_view(), name="me-bookmarks"),
]
