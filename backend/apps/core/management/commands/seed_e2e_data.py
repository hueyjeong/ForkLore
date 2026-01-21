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

        # Create additional authors for ranking tests (20 authors total)
        author_names = [
            "Elena",
            "JinWoo",
            "Aria",
            "Luna",
            "Marcus",
            "Sophie",
            "Kai",
            "Yuna",
            "Oliver",
            "Emma",
            "Liam",
            "Mia",
            "Noah",
            "Ava",
            "Ethan",
            "Isabella",
            "Lucas",
            "Zoe",
            "Mason",
        ]
        authors = [author]
        for name in author_names:
            authors.append(
                self._create_user(
                    email=f"{name.lower()}@example.com",
                    username=name.lower(),
                    nickname=name,
                    password="testpassword123",
                    role="AUTHOR",
                )
            )

        # Create 50 novels for infinite scroll testing
        genres = ["FANTASY", "ROMANCE", "ACTION", "THRILLER", "MYSTERY", "SF", "MARTIAL"]
        novels = []
        for i in range(1, 51):
            is_premium = i % 10 == 1
            is_exclusive = i % 10 == 2
            novel = self._create_novel(
                author=authors[i % len(authors)],
                title=f"Test Novel {i}",
                genre=genres[i % len(genres)],
                is_premium=is_premium,
                is_exclusive=is_exclusive,
            )
            novels.append(novel)

            # Create main branch with 20 chapters for first 10 novels, 5 for others
            main_branch = self._create_main_branch(novel, authors[i % len(authors)])
            chapter_count = 20 if i <= 10 else 5
            self._create_chapters(main_branch, count=chapter_count)

            # Create fork branches only for first 10 novels
            if i <= 10:
                for j in range(1, 3):
                    fork_branch = self._create_fork_branch(
                        novel=novel,
                        parent_branch=main_branch,
                        author=reader if j == 1 else authors[(i + j) % len(authors)],
                        name=f"Fork {j} of {novel.title}",
                        fork_point=2,
                    )
                    self._create_chapters(fork_branch, count=5)

        # Create interactions for first novel
        first_novel = novels[0]
        first_branch = first_novel.branches.filter(is_main=True).first()
        if first_branch:
            first_chapter = first_branch.chapters.first()
            if first_chapter:
                self._create_interactions(reader, first_chapter)

        # Create wallets and transactions
        self._create_wallets_and_transactions(reader, authors)

        # Create subscriptions
        self._create_subscriptions(reader)

        # Create purchases
        if first_branch:
            paid_chapter = first_branch.chapters.filter(chapter_number=3).first()
            if paid_chapter:
                self._create_purchases(reader, paid_chapter)

        # Create likes
        if first_branch:
            self._create_likes(reader, first_branch.chapters.first())

        # Create wiki entries and maps for first branch
        if first_branch:
            self._create_wiki_entries(first_branch, author)
            self._create_maps(first_branch, author)

        # Create AI usage logs
        self._create_ai_usage_logs(reader)

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

    def _create_novel(
        self,
        author: User,
        title: str,
        genre: str,
        is_premium: bool = False,
        is_exclusive: bool = False,
    ):
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
                "is_premium": is_premium,
                "is_exclusive": is_exclusive,
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

    def _create_wallets_and_transactions(self, reader: User, authors: list) -> None:
        from apps.interactions.models import CoinTransaction, TransactionType, Wallet

        for user in [reader] + authors:
            wallet, created = Wallet.objects.get_or_create(
                user=user,
                defaults={"balance": 1000 if user == reader else 500},
            )
            if created:
                self.stdout.write(f"    Created wallet for {user.nickname}")
                CoinTransaction.objects.create(
                    wallet=wallet,
                    transaction_type=TransactionType.CHARGE,
                    amount=wallet.balance,
                    balance_after=wallet.balance,
                    description="Initial E2E test balance",
                )

    def _create_subscriptions(self, reader: User) -> None:
        from datetime import timedelta

        from apps.interactions.models import PlanType, Subscription, SubscriptionStatus

        sub, created = Subscription.objects.get_or_create(
            user=reader,
            defaults={
                "plan_type": PlanType.PREMIUM,
                "expires_at": timezone.now() + timedelta(days=30),
                "payment_id": "test_payment_001",
                "auto_renew": True,
                "status": SubscriptionStatus.ACTIVE,
            },
        )
        if created:
            self.stdout.write(f"    Created subscription for {reader.nickname}")

    def _create_purchases(self, reader: User, chapter) -> None:
        from apps.interactions.models import Purchase

        purchase, created = Purchase.objects.get_or_create(
            user=reader,
            chapter=chapter,
            defaults={"price_paid": 100},
        )
        if created:
            self.stdout.write(f"    Created purchase for chapter {chapter.chapter_number}")

    def _create_likes(self, reader: User, chapter) -> None:
        from django.contrib.contenttypes.models import ContentType

        from apps.interactions.models import Like

        content_type = ContentType.objects.get_for_model(chapter)
        like, created = Like.objects.get_or_create(
            user=reader,
            content_type=content_type,
            object_id=chapter.id,
        )
        if created:
            self.stdout.write(f"    Created like for chapter {chapter.chapter_number}")

    def _create_wiki_entries(self, branch, author: User) -> None:
        from apps.contents.models import WikiEntry, WikiSnapshot, WikiTagDefinition

        tag, _ = WikiTagDefinition.objects.get_or_create(
            branch=branch,
            name="캐릭터",
            defaults={"color": "#FF5733", "icon": "user", "description": "등장인물"},
        )

        wiki, created = WikiEntry.objects.get_or_create(
            branch=branch,
            name="주인공",
            defaults={
                "image_url": "",
                "first_appearance": 1,
                "hidden_note": "비밀 메모",
            },
        )
        if created:
            wiki.tags.add(tag)
            WikiSnapshot.objects.create(
                wiki_entry=wiki,
                content="주인공에 대한 설명입니다.",
                valid_from_chapter=1,
                contributor=author,
            )
            self.stdout.write(f"    Created wiki entry: {wiki.name}")

    def _create_maps(self, branch, author: User) -> None:
        from apps.contents.models import (
            LayerType,
            Map,
            MapLayer,
            MapObject,
            MapSnapshot,
            ObjectType,
        )

        map_obj, created = Map.objects.get_or_create(
            branch=branch,
            name="세계 지도",
            defaults={
                "description": "소설 세계의 전체 지도",
                "width": 1000,
                "height": 800,
            },
        )
        if created:
            snapshot = MapSnapshot.objects.create(
                map=map_obj,
                valid_from_chapter=1,
                base_image_url="",
            )
            layer = MapLayer.objects.create(
                snapshot=snapshot,
                name="기본 레이어",
                layer_type=LayerType.BASE,
                z_index=0,
            )
            MapObject.objects.create(
                layer=layer,
                object_type=ObjectType.POINT,
                coordinates={"x": 500, "y": 400},
                label="시작 마을",
                description="주인공이 처음 등장하는 마을",
            )
            self.stdout.write(f"    Created map: {map_obj.name}")

    def _create_ai_usage_logs(self, reader: User) -> None:
        from apps.interactions.models import AIActionType, AIUsageLog

        log, created = AIUsageLog.objects.get_or_create(
            user=reader,
            usage_date=timezone.now().date(),
            action_type=AIActionType.WIKI_SUGGEST,
            defaults={"request_count": 5, "token_count": 1500},
        )
        if created:
            self.stdout.write(f"    Created AI usage log for {reader.nickname}")

    def _get_summary(self) -> str:
        from apps.contents.models import Chapter, Map, WikiEntry
        from apps.interactions.models import (
            AIUsageLog,
            Bookmark,
            Comment,
            Like,
            Purchase,
            Subscription,
            Wallet,
        )
        from apps.novels.models import Branch, Novel

        return (
            f"\nE2E Seed Data Summary:\n"
            f"  Users: {User.objects.count()}\n"
            f"  Novels: {Novel.objects.count()}\n"
            f"  Branches: {Branch.objects.count()}\n"
            f"  Chapters: {Chapter.objects.count()}\n"
            f"  Bookmarks: {Bookmark.objects.count()}\n"
            f"  Comments: {Comment.objects.count()}\n"
            f"  Likes: {Like.objects.count()}\n"
            f"  Wallets: {Wallet.objects.count()}\n"
            f"  Subscriptions: {Subscription.objects.count()}\n"
            f"  Purchases: {Purchase.objects.count()}\n"
            f"  WikiEntries: {WikiEntry.objects.count()}\n"
            f"  Maps: {Map.objects.count()}\n"
            f"  AIUsageLogs: {AIUsageLog.objects.count()}\n"
        )
