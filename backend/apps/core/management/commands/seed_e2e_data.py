"""
Management command to seed E2E test data.

Creates predictable, deterministic test data for E2E testing.
Uses model_bakery for data creation with fixed values.

Usage:
    DJANGO_SETTINGS_MODULE=config.settings.e2e python manage.py seed_e2e_data
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from model_bakery import baker

User = get_user_model()


class Command(BaseCommand):
    help = "Seed database with E2E test data"

    def handle(self, *args, **options) -> None:
        self.stdout.write("Seeding E2E test data...")

        # Create test users
        reader = self._create_user(
            email="testreader@example.com",
            username="testreader",
            nickname="TestReader",
            password="testpassword123",
            role="READER",
        )

        author = self._create_user(
            email="testauthor@example.com",
            username="testauthor",
            nickname="TestAuthor",
            password="testpassword123",
            role="AUTHOR",
        )

        # Create additional authors for ranking tests
        author_names = ["Elena", "JinWoo", "Aria", "Luna"]
        authors = [author]
        for i, name in enumerate(author_names):
            authors.append(
                self._create_user(
                    email=f"{name.lower()}@example.com",
                    username=name.lower(),
                    nickname=name,
                    password="testpassword123",
                    role="AUTHOR",
                )
            )

        # Create novels
        novels = []
        for i in range(1, 6):
            novel = self._create_novel(
                author=authors[i % len(authors)],
                title=f"Test Novel {i}",
                genre="FANTASY" if i % 2 == 0 else "ROMANCE",
            )
            novels.append(novel)

            # Create main branch and chapters
            main_branch = self._create_main_branch(novel, authors[i % len(authors)])
            self._create_chapters(main_branch, count=5)

            # Create 2 fork branches per novel
            for j in range(1, 3):
                fork_branch = self._create_fork_branch(
                    novel=novel,
                    parent_branch=main_branch,
                    author=reader if j == 1 else authors[(i + j) % len(authors)],
                    name=f"Fork {j} of {novel.title}",
                    fork_point=2,
                )
                self._create_chapters(fork_branch, count=3)

        # Create interactions for first novel
        first_novel = novels[0]
        first_branch = first_novel.branches.filter(is_main=True).first()
        if first_branch:
            first_chapter = first_branch.chapters.first()
            if first_chapter:
                self._create_interactions(reader, first_chapter)

        self.stdout.write(self.style.SUCCESS(self._get_summary()))

    def _create_user(
        self,
        email: str,
        username: str,
        nickname: str,
        password: str,
        role: str,
    ) -> User:
        """Create a user if not exists."""
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": username,
                "nickname": nickname,
                "role": role,
            },
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(f"  Created user: {email}")
        else:
            self.stdout.write(f"  User exists: {email}")
        return user

    def _create_novel(self, author: User, title: str, genre: str):
        """Create a novel if not exists."""
        from apps.novels.models import Novel

        novel, created = Novel.objects.get_or_create(
            author=author,
            title=title,
            defaults={
                "description": f"Description for {title}",
                "genre": genre,
                "age_rating": "ALL",
                "status": "ONGOING",
                "allow_branching": True,
            },
        )
        if created:
            self.stdout.write(f"  Created novel: {title}")
        return novel

    def _create_main_branch(self, novel, author: User):
        """Create main branch for a novel if not exists."""
        from apps.novels.models import Branch

        branch, created = Branch.objects.get_or_create(
            novel=novel,
            is_main=True,
            defaults={
                "author": author,
                "name": novel.title,
                "description": f"Main story of {novel.title}",
                "branch_type": "MAIN",
                "visibility": "PUBLIC",
            },
        )
        if created:
            self.stdout.write(f"    Created main branch: {branch.name}")
        return branch

    def _create_fork_branch(
        self,
        novel,
        parent_branch,
        author: User,
        name: str,
        fork_point: int,
    ):
        """Create a fork branch if not exists."""
        from apps.novels.models import Branch

        branch, created = Branch.objects.get_or_create(
            novel=novel,
            name=name,
            defaults={
                "author": author,
                "parent_branch": parent_branch,
                "fork_point_chapter": fork_point,
                "is_main": False,
                "description": f"Fork from chapter {fork_point}",
                "branch_type": "FAN_FIC",
                "visibility": "PUBLIC",
            },
        )
        if created:
            self.stdout.write(f"    Created fork branch: {name}")
        return branch

    def _create_chapters(self, branch, count: int) -> None:
        """Create chapters for a branch if not exists."""
        from apps.contents.models import Chapter

        for i in range(1, count + 1):
            chapter, created = Chapter.objects.get_or_create(
                branch=branch,
                chapter_number=i,
                defaults={
                    "title": f"Chapter {i}",
                    "content": f"# Chapter {i}\n\nThis is the content of chapter {i} for {branch.name}.\n\n"
                    f"Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                    f"Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "content_html": f"<h1>Chapter {i}</h1><p>This is the content of chapter {i}.</p>",
                    "word_count": 50,
                    "status": "PUBLISHED",
                    "access_type": "FREE",
                    "published_at": timezone.now(),
                },
            )
            if created:
                self.stdout.write(f"      Created chapter: {i}")

    def _create_interactions(self, user: User, chapter) -> None:
        """Create sample interactions for a chapter."""
        from apps.interactions.models import Bookmark, Comment

        # Create bookmark
        bookmark, created = Bookmark.objects.get_or_create(
            user=user,
            chapter=chapter,
            defaults={
                "scroll_position": 0.5,
                "note": "Interesting part",
            },
        )
        if created:
            self.stdout.write(f"    Created bookmark for chapter {chapter.chapter_number}")

        # Create comment
        comment, created = Comment.objects.get_or_create(
            user=user,
            chapter=chapter,
            content="This is a test comment for E2E testing.",
            defaults={
                "is_spoiler": False,
            },
        )
        if created:
            self.stdout.write(f"    Created comment for chapter {chapter.chapter_number}")

    def _get_summary(self) -> str:
        """Get summary of created data."""
        from apps.contents.models import Chapter
        from apps.interactions.models import Bookmark, Comment
        from apps.novels.models import Branch, Novel

        return (
            f"\nE2E Seed Data Summary:\n"
            f"  Users: {User.objects.count()}\n"
            f"  Novels: {Novel.objects.count()}\n"
            f"  Branches: {Branch.objects.count()}\n"
            f"  Chapters: {Chapter.objects.count()}\n"
            f"  Bookmarks: {Bookmark.objects.count()}\n"
            f"  Comments: {Comment.objects.count()}\n"
        )
