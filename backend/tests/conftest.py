import pytest
from model_bakery import baker


@pytest.fixture
def user(db):
    return baker.make("users.User", email="test@example.com", nickname="testuser")


@pytest.fixture
def author(db):
    return baker.make("users.User", email="author@example.com", nickname="author", role="AUTHOR")


@pytest.fixture
def novel(db, author):
    return baker.make("novels.Novel", author=author, title="테스트 소설")


@pytest.fixture
def main_branch(db, novel, author):
    return baker.make(
        "novels.Branch",
        novel=novel,
        author=author,
        name=novel.title,
        is_main=True,
        branch_type="MAIN",
    )


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client
