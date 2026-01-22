"""
Django management command for seeding test data.

This command creates realistic test data for all models across all apps
(users, novels, contents, interactions) in ForkLore backend.

Usage:
    poetry run python manage.py seed_db [--force] [--scale=N] [--seed=INTEGER]
"""

import random
from datetime import timedelta
from typing import Any

from django.contrib.auth.hashers import make_password
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.contents.models import (
    AccessType,
    Chapter,
    ChapterStatus,
    ContributorType,
    LayerType,
    Map,
    MapLayer,
    MapObject,
    MapSnapshot,
    ObjectType,
    WikiEntry,
    WikiSnapshot,
    WikiTagDefinition,
)
from apps.interactions.models import (
    AIActionType,
    AIUsageLog,
    Bookmark,
    CoinTransaction,
    Comment,
    Like,
    PlanType,
    Purchase,
    ReadingLog,
    Report,
    ReportReason,
    ReportStatus,
    Subscription,
    SubscriptionStatus,
    TransactionType,
    Wallet,
)
from apps.novels.models import (
    AgeRating,
    Branch,
    BranchLinkRequest,
    BranchType,
    BranchVisibility,
    BranchVote,
    CanonStatus,
    Genre,
    Novel,
    NovelStatus,
)
from apps.users.models import AuthProvider, User, UserRole

# =============================================================================
# Data Generators
# =============================================================================


class KoreanDataGenerator:
    """Generate realistic Korean content for test data."""

    NOVEL_TITLES = [
        "검은 마법사의 눈물",
        "시간을 멈춘 마을",
        "용사의 귀환",
        "별빛 기사단",
        "마지막 제국",
        "붉은 달의 전설",
        "나무 사이의 비밀",
        "바람의 검객",
        "눈물의 성",
        "천년의 계약",
        "어둠의 기사",
        "빛의 전사",
        "마법의 학교",
        "드래곤 라이더",
        "영웅의 길",
    ]

    NOVEL_DESCRIPTIONS = [
        "이세계에서 펼쳐지는 신비로운 모험이 시작된다.",
        "운명의 용사가 어둠과 빛의 전쟁에 휘말린다.",
        "마법사가 자신의 잃어버린 기억을 찾아 여정을 떠난다.",
        "제국의 멸망과 새로운 희망의 탄생을 그린 서사시.",
        "고대의 전설이 현대에 깨어난다.",
        "용사와 마법사가 함께 세상을 구하는 이야기.",
        "사랑과 배신, 우정과 희생이 얽힌 대장정.",
        "어둠 속에서 빛을 찾는 이들의 투쟁.",
        "천 년의 저주가 풀리고 새로운 시대가 열린다.",
        "별의 인도를 받은 선택된 자들의 이야기.",
    ]

    BRANCH_NAMES = [
        "메인 스토리",
        "히로인의 시점",
        "빌런의 과거",
        "액손딩 스토리",
        "IF 루트: 다른 선택",
        "마법사의 비망록",
        "제2의 영웅",
        "어둠의 길",
        "빛의 길",
        "새로운 시작",
    ]

    BRANCH_DESCRIPTIONS = [
        "메인 스토리의 공식 라인입니다.",
        "주요 인물의 다른 관점에서 이야기를 서술합니다.",
        "어떤 선택이 다른 결과를 낳는지 탐구합니다.",
        "원작에서 다루지 않은 에피소드를 담았습니다.",
        "만약 다른 선택을 했다면 어떻게 되었을까요?",
        "마법과 비밀의 세계로 초대합니다.",
    ]

    CHAPTER_TITLES = [
        "새로운 시작",
        "운명의 만남",
        "첫 번째 시련",
        "숨겨진 비밀",
        "마법의 발견",
        "동료와의 결속",
        "어둠의 그림자",
        "빛의 희망",
        "과거의 유령",
        "미래의 약속",
        "결전의 서막",
        "최후의 선택",
        "새로운 여정",
        "마지막 전쟁",
        "평화의 도래",
    ]

    WIKI_ENTRY_NAMES = [
        "마법검 엑스칼리버",
        "불의 정령 이프리트",
        "어둠의 성",
        "빛의 탑",
        "용의 알",
        "고대의 두루마리",
        "신비의 약초",
        "마법의 수정",
        "검은 갑주",
        "희망의 반지",
        "영웅의 검",
        "마법사의 지팡이",
        "용사의 방패",
        "신성한 성검",
        "시간의 모래시계",
    ]

    MAP_NAMES = [
        "제국 지도",
        "마법 학교",
        "전설의 던전",
        "용의 둥지",
        "신비의 숲",
        "잃어버린 왕국",
        "마법사의 탑",
        "해적의 섬",
        "눈의 왕국",
        "화산 지대",
    ]

    TAG_NAMES = [
        "캐릭터",
        "장소",
        "아이템",
        "마법",
        "조직",
        "종족",
        "신화",
        "역사",
        "사건",
        "개념",
    ]

    USER_NICKNAMES = [
        "은빛용사",
        "어둠의마법사",
        "별빛검객",
        "바람의궁수",
        "불의주술사",
        "시간의여행자",
        "빛의기사",
        "그림자암살자",
        "천둥의용사",
        "물의정령",
        "숲의지킴이",
        "마법의학생",
        "검은기사",
        "흰마법사",
        "하늘의날개",
    ]

    COMMENT_CONTENTS = [
        "이번 회차 진짜 재밌었어요!",
        "작가님 대박입니다 ㅋㅋㅋ",
        "주인공이 이렇게 바뀌다니...",
        "다음 회차 기대됩니다!",
        "반전 진짜 좋네요",
        "여기서 울었음 ㅠㅠ",
        "마지막 장면이 영상 같아요",
        "이 소설 진짜 추천합니다",
        "빨리 다음 회차 써주세요",
        "작가님 감사합니다 ❤️",
        "평점 10점 드립니다",
        "이거 왜 이렇게 잘 쓰셨죠?",
        "올해 최고의 소설",
        "매일 새벽에 기다리는 소설",
        "작가님 파이팅!",
    ]

    CHAPTER_CONTENTS = [
        """# {title}

## 시작
어둠의 그림자가 드리운 성문 앞에서, 한 소년이 서 있었다. 그의 눈빛은 결의로 가득 차 있었고, 손에 든 낡은 검은 여전히 빛나고 있었다.

## 발견
소년은 우연히 고대의 유적을 발견했다. 그곳에는 잊혀진 마법이 잠들어 있었다. 마법사의 두루마리를 펼치자, 신비로운 빛이 그를 감쌌다.

## 시련
첫 번째 시련은 강철의 거인이었다. 소년은 자신의 모든 힘을 다해 싸웠지만, 상대가 너무 강했다. 그러던 중, 그는 마법의 힘을 깨닫게 되었다.

## 결말
마법의 힘으로 거인을 물리치고, 소년은 새로운 길로 나아갔다. 그의 여정은 이제 막 시작이었다.
""",
        """# {title}

## 여정의 시작
용사는 마을을 떠나기로 결심했다. 그의 가방에는 소중한 아이템과 동료들의 축복이 담겨 있었다.

## 만남
길에서 만난 의문의 여인은 용사에게 중요한 정보를 알려주었다. "어둠의 성에서는 위험한 일이 벌어지고 있어요."

## 전투
마물들이 나타났다. 용사는 검을 뽑아 들고 맞섰다. 검은 빛이 마물들을 베어버렸다.

## 새로운 동료
전투 중에 만난 마법사가 동료로 합류했다. 함께라면 어떤 시련도 이겨낼 수 있을 것 같았다.
""",
        """# {title}

## 비밀의 방
마법 학교의 지하 깊은 곳에는 잠겨진 방이 있었다. 그곳에는 고대의 비밀이 숨겨져 있었다.

## 발견
학생들은 우연히 그 방의 열쇠를 찾았다. 문을 열자, 놀라운 장면이 펼쳐졌다.

## 경고
"이곳의 비밀은 누구에게도 말하지 마라." 교수의 목소리가 들려왔다.

## 선택
학생들은 비밀을 지키기로 결심했다. 그러나 누군가는 다른 선택을 하려 하고 있었다...
""",
    ]

    REPORT_DESCRIPTIONS = [
        "부적절한 내용이 포함되어 있습니다.",
        "저작권 위반이 의심됩니다.",
        "욕설과 비방이 있습니다.",
        "스포일러가 포함되어 있습니다.",
        "스팸성 댓글입니다.",
    ]

    TRANSACTION_DESCRIPTIONS = [
        "코인 충전",
        "회차 구매",
        "환불 처리",
        "프로모션 지급",
        "정산 조정",
    ]

    AI_ACTION_DESCRIPTIONS = [
        "위키 제안 생성",
        "일관성 검사 수행",
        "AI 질문 응답",
    ]

    @classmethod
    def random_choice(cls, choices: list[Any] | tuple[Any, ...]) -> Any:
        """Return a random choice from a list."""
        return random.choice(choices)

    @classmethod
    def random_int(cls, min_val: int, max_val: int) -> int:
        """Return a random integer between min and max (inclusive)."""
        return random.randint(min_val, max_val)

    @classmethod
    def random_bool(cls) -> bool:
        """Return a random boolean."""
        return random.choice([True, False])

    @classmethod
    def weighted_choice(cls, choices: list[Any], weights: list[int] | list[float]) -> Any:
        """Return a random choice with weighted probability."""
        return random.choices(choices, weights=weights, k=1)[0]


# =============================================================================
# Seed Command
# =============================================================================


class Command(BaseCommand):
    help = "Seed the database with test data."

    def add_arguments(self, parser: Any) -> None:
        """Add command-line arguments."""
        parser.add_argument(
            "--force",
            action="store_true",
            help="Clear existing data before seeding",
        )
        parser.add_argument(
            "--scale",
            type=int,
            default=1,
            help="Scale factor for data amount (default: 1)",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=None,
            help="Random seed for reproducible data generation",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Handle command execution."""
        force = options["force"]
        scale = options["scale"]
        seed = options["seed"]

        if scale < 1:
            raise CommandError("Scale factor must be >= 1")

        if seed is not None:
            random.seed(seed)
            self.stdout.write(f"Using random seed: {seed}")

        if force:
            self.stdout.write(self.style.WARNING("Clearing existing data..."))
            self._clear_all_data()

        self.stdout.write(self.style.SUCCESS(f"Seeding database with scale={scale}..."))
        stats = self._seed_data(scale)
        self._print_summary(stats)

    @transaction.atomic
    def _clear_all_data(self) -> None:
        """Clear all data in reverse order of creation."""
        # Interactions (reverse order)
        AIUsageLog.objects.all().delete()
        CoinTransaction.objects.all().delete()
        Wallet.objects.all().delete()
        Report.objects.all().delete()
        Like.objects.all().delete()
        Comment.objects.all().delete()
        Bookmark.objects.all().delete()
        ReadingLog.objects.all().delete()
        Purchase.objects.all().delete()
        Subscription.objects.all().delete()

        # Contents (reverse order)
        MapObject.objects.all().delete()
        MapLayer.objects.all().delete()
        MapSnapshot.objects.all().delete()
        Map.objects.all().delete()
        WikiSnapshot.objects.all().delete()
        WikiEntry.objects.all().delete()
        WikiTagDefinition.objects.all().delete()
        Chapter.objects.all().delete()

        # Novels (reverse order)
        BranchLinkRequest.objects.all().delete()
        BranchVote.objects.all().delete()
        Branch.objects.all().delete()
        Novel.objects.all().delete()

        # Users
        User.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("All data cleared"))

    @transaction.atomic
    def _seed_data(self, scale: int) -> dict[str, int]:
        """Seed all data respecting foreign key dependencies."""
        stats = {}

        # 1. Users
        self.stdout.write("Creating users...")
        num_users = 10 * scale
        users = self._create_users(num_users)
        stats["users"] = len(users)

        # 2. Novels and main branches
        self.stdout.write("Creating novels...")
        num_novels = 80 * scale
        novels, main_branches = self._create_novels_with_main_branches(
            users[: num_users // 2], num_novels
        )
        stats["novels"] = len(novels)
        stats["main_branches"] = len(main_branches)

        # 3. Side branches (forks)
        self.stdout.write("Creating side branches...")
        num_side_branches = 30 * scale
        side_branches = self._create_side_branches(users, main_branches, num_side_branches)
        stats["side_branches"] = len(side_branches)

        all_branches = list(main_branches) + side_branches

        # 4. Chapters - novel-based approach
        self.stdout.write("Creating chapters...")
        chapters = self._create_chapters_for_novels(
            novels,
            main_branches,
            side_branches,
            large_novel_count=15,
            min_chapters_per_novel=3,
        )
        stats["chapters"] = len(chapters)

        # 5. Wiki entries and snapshots
        self.stdout.write("Creating wiki entries...")
        num_wikis = 20 * scale
        wiki_entries = self._create_wiki_entries(all_branches, num_wikis, chapters)
        stats["wiki_entries"] = len(wiki_entries)

        # 6. Maps, layers, and objects
        self.stdout.write("Creating maps...")
        num_maps = 5 * scale
        maps = self._create_maps(all_branches, num_maps, chapters)
        stats["maps"] = len(maps)

        # 7. Interactions
        self.stdout.write("Creating interactions...")
        interaction_stats = self._create_interactions(users, chapters, all_branches)
        stats.update(interaction_stats)

        # 8. Wallet and transactions
        self.stdout.write("Creating wallets and transactions...")
        wallet_stats = self._create_wallets_and_transactions(users)
        stats.update(wallet_stats)

        # 9. AI usage logs
        self.stdout.write("Creating AI usage logs...")
        num_ai_logs = 30 * scale
        ai_logs = self._create_ai_usage_logs(users, num_ai_logs)
        stats["ai_usage_logs"] = len(ai_logs)

        return stats

    # =========================================================================
    # User Creation
    # =========================================================================

    def _create_users(self, count: int) -> list[User]:
        """Create test users."""
        users = []
        for i in range(count):
            is_author = i < count // 2  # First half are authors
            role = UserRole.AUTHOR if is_author else UserRole.READER

            # Use get_or_create to avoid duplicates when running without --force
            user, created = User.objects.get_or_create(
                email=f"user{i + 1}@example.com",
                defaults={
                    "username": f"user{i + 1}",
                    "nickname": KoreanDataGenerator.random_choice(
                        KoreanDataGenerator.USER_NICKNAMES
                    )
                    + f"{i + 1:02d}",
                    "password": make_password("password123"),
                    "role": role,
                    "auth_provider": AuthProvider.LOCAL,
                    "bio": f"테스트 사용자 {i + 1}입니다.",
                    "profile_image_url": f"https://example.com/avatars/{i + 1}.jpg",
                    "mileage": KoreanDataGenerator.random_int(0, 10000),
                    "coin": KoreanDataGenerator.random_int(0, 5000),
                    "email_verified": True,
                },
            )
            users.append(user)

        # Create one admin user
        admin, created = User.objects.get_or_create(
            email="admin@example.com",
            defaults={
                "username": "admin",
                "nickname": "관리자",
                "password": make_password("admin123"),
                "role": UserRole.ADMIN,
                "auth_provider": AuthProvider.LOCAL,
                "bio": "시스템 관리자",
                "profile_image_url": "https://example.com/avatars/admin.jpg",
                "mileage": 999999,
                "coin": 999999,
                "email_verified": True,
            },
        )
        if created:
            users.append(admin)

        return users

    # =========================================================================
    # Novel and Branch Creation
    # =========================================================================

    def _create_novels_with_main_branches(
        self, authors: list[User], count: int
    ) -> tuple[list[Novel], list[Branch]]:
        """Create novels with their main branches."""
        novels_to_create = []
        main_branches_to_create = []

        for i in range(count):
            author = KoreanDataGenerator.random_choice(authors)

            novel = Novel(
                author=author,
                title=KoreanDataGenerator.random_choice(KoreanDataGenerator.NOVEL_TITLES)
                + f" {i + 1}",
                description=KoreanDataGenerator.random_choice(
                    KoreanDataGenerator.NOVEL_DESCRIPTIONS
                ),
                cover_image_url=f"https://example.com/covers/novel{i + 1}.jpg",
                genre=KoreanDataGenerator.random_choice(list(Genre.choices))[0],
                age_rating=KoreanDataGenerator.random_choice(list(AgeRating.choices))[0],
                status=KoreanDataGenerator.weighted_choice(
                    list(NovelStatus.choices),
                    [0.6, 0.3, 0.1],  # ONGOING 60%, COMPLETED 30%, HIATUS 10%
                )[0],
                allow_branching=KoreanDataGenerator.random_bool(),
                is_exclusive=KoreanDataGenerator.random_bool(),
                is_premium=KoreanDataGenerator.random_bool(),
                total_view_count=KoreanDataGenerator.random_int(0, 100000),
                total_like_count=KoreanDataGenerator.random_int(0, 10000),
                total_chapter_count=0,
                branch_count=1,
                linked_branch_count=0,
            )
            novels_to_create.append(novel)

            # Create main branch
            main_branch = Branch(
                novel=novel,
                author=author,
                is_main=True,
                parent_branch=None,
                fork_point_chapter=None,
                name="메인 스토리",
                description=KoreanDataGenerator.random_choice(
                    KoreanDataGenerator.BRANCH_DESCRIPTIONS
                ),
                cover_image_url=novel.cover_image_url,
                branch_type=BranchType.MAIN,
                visibility=BranchVisibility.PUBLIC,
                canon_status=CanonStatus.NON_CANON,
                merged_at_chapter=None,
                vote_count=KoreanDataGenerator.random_int(0, 5000),
                vote_threshold=1000,
                view_count=KoreanDataGenerator.random_int(0, 50000),
                chapter_count=0,
                version=1,
            )
            main_branches_to_create.append(main_branch)

        # Bulk create novels and main branches
        novels = Novel.objects.bulk_create(novels_to_create)
        main_branches = Branch.objects.bulk_create(main_branches_to_create)

        return novels, main_branches

    def _create_side_branches(
        self, users: list[User], main_branches: list[Branch], count: int
    ) -> list[Branch]:
        """Create side branches (forks)."""
        side_branches_to_create = []

        for i in range(count):
            parent_branch = KoreanDataGenerator.random_choice(main_branches)
            author = KoreanDataGenerator.random_choice(users)

            branch = Branch(
                novel=parent_branch.novel,
                author=author,
                is_main=False,
                parent_branch=parent_branch,
                fork_point_chapter=KoreanDataGenerator.random_int(1, 10),
                name=KoreanDataGenerator.random_choice(KoreanDataGenerator.BRANCH_NAMES)
                + f" {i + 1}",
                description=KoreanDataGenerator.random_choice(
                    KoreanDataGenerator.BRANCH_DESCRIPTIONS
                ),
                cover_image_url=f"https://example.com/covers/branch{i + 1}.jpg",
                branch_type=KoreanDataGenerator.random_choice(
                    [BranchType.SIDE_STORY, BranchType.FAN_FIC, BranchType.IF_STORY]
                ),
                visibility=KoreanDataGenerator.weighted_choice(
                    list(BranchVisibility.choices),
                    [0.6, 0.3, 0.1],  # PUBLIC 60%, PRIVATE 30%, LINKED 10%
                )[0],
                canon_status=KoreanDataGenerator.random_choice(list(CanonStatus.choices))[0],
                merged_at_chapter=None,
                vote_count=KoreanDataGenerator.random_int(0, 500),
                vote_threshold=1000,
                view_count=KoreanDataGenerator.random_int(0, 50000),
                chapter_count=0,
                version=1,
            )
            side_branches_to_create.append(branch)

        # Bulk create side branches
        side_branches = Branch.objects.bulk_create(side_branches_to_create)

        # Bulk update novel branch counts after all branches are created
        for novel in {b.novel for b in side_branches_to_create}:
            novel.branch_count = Branch.objects.filter(novel=novel).count()
            novel.save(update_fields=["branch_count"])

        return side_branches

    # =========================================================================
    # Chapter Creation
    # =========================================================================

    def _create_chapters_for_novels(
        self,
        novels: list[Novel],
        main_branches: list[Branch],
        side_branches: list[Branch],
        large_novel_count: int = 15,
        min_chapters_per_novel: int = 3,
    ) -> list[Chapter]:
        """Create chapters for novels with novel-based distribution.

        Args:
            novels: List of novels
            main_branches: List of main branches (one per novel)
            side_branches: List of side branches
            large_novel_count: Number of novels to have 100+ chapters
            min_chapters_per_novel: Minimum chapters for other novels

        Returns:
            List of created chapters
        """
        chapters = []

        # Create a mapping from novel to its branches
        novel_to_branches: dict[Novel, list[Branch]] = {}
        for branch in list(main_branches) + side_branches:
            if branch.novel not in novel_to_branches:
                novel_to_branches[branch.novel] = []
            novel_to_branches[branch.novel].append(branch)

        # Select novels that will have many chapters
        large_novels = set(random.sample(novels, min(large_novel_count, len(novels))))

        for novel in novels:
            novel_branches = novel_to_branches[novel]
            main_branch = next(
                b for b in novel_branches if b.is_main
            )  # Explicitly find main branch

            if novel in large_novels:
                # Create 100+ chapters for large novels (split across branches)
                total_chapters_for_novel = KoreanDataGenerator.random_int(100, 150)

                # 70% on main branch, 30% on side branches
                main_branch_chapters = int(total_chapters_for_novel * 0.7)
                side_chapters_total = total_chapters_for_novel - main_branch_chapters

                # Create chapters for main branch
                for chapter_num in range(1, main_branch_chapters + 1):
                    chapter = self._create_single_chapter(main_branch, chapter_num)
                    chapters.append(chapter)

                # Create chapters for side branches (if any)
                if len(novel_branches) > 1:
                    side_branches_for_novel = novel_branches[1:]
                    chapters_per_side = side_chapters_total // len(side_branches_for_novel)

                    for branch in side_branches_for_novel:
                        for chapter_num in range(1, chapters_per_side + 1):
                            chapter = self._create_single_chapter(branch, chapter_num)
                            chapters.append(chapter)

                total_chapters_for_novel = len([c for c in chapters if c.branch.novel == novel])

                self.stdout.write(
                    f"  - Created {total_chapters_for_novel} chapters for large novel: {novel.title}"
                )
            else:
                # Create minimum chapters for regular novels
                num_chapters = KoreanDataGenerator.random_int(
                    min_chapters_per_novel, min_chapters_per_novel + 10
                )

                # Most chapters on main branch, few on side branches
                main_branch_chapters = int(num_chapters * 0.8)

                # Create chapters for main branch
                for chapter_num in range(1, main_branch_chapters + 1):
                    chapter = self._create_single_chapter(main_branch, chapter_num)
                    chapters.append(chapter)

                total_chapters_for_novel = len([c for c in chapters if c.branch.novel == novel])

        # Update branch chapter_count using bulk_update
        # Collect all branches with their chapter counts
        branches_to_update = []
        for novel in novels:
            novel_branches = novel_to_branches[novel]
            # Count chapters per branch
            for branch in novel_branches:
                branch.chapter_count = len([c for c in chapters if c.branch_id == branch.id])
                branches_to_update.append(branch)

        # Bulk update all branch chapter_count
        Branch.objects.bulk_update(
            branches_to_update,
            ["chapter_count"],
            batch_size=500
        )

        return chapters
            else:
                # Create minimum chapters for regular novels
                num_chapters = KoreanDataGenerator.random_int(
                    min_chapters_per_novel, min_chapters_per_novel + 10
                )

                # Most chapters on main branch, few on side branches
                main_branch_chapters = int(num_chapters * 0.8)
                side_chapters_total = num_chapters - main_branch_chapters

                # Create chapters for main branch
                for chapter_num in range(1, main_branch_chapters + 1):
                    chapter = self._create_single_chapter(main_branch, chapter_num)
                    chapters.append(chapter)

                # Create chapters for side branches (if any)
                if len(novel_branches) > 1:
                    side_branches_for_novel = novel_branches[1:]
                    if side_branches_for_novel:
                        chapters_per_side = max(
                            1, side_chapters_total // len(side_branches_for_novel)
                        )
                        for branch in side_branches_for_novel:
                            for chapter_num in range(1, chapters_per_side + 1):
                                chapter = self._create_single_chapter(branch, chapter_num)
                                chapters.append(chapter)

        # Update branch chapter counts in bulk
        for novel in novels:
            for branch in novel_to_branches[novel]:
                branch.chapter_count = Chapter.objects.filter(branch=branch).count()
                branch.save(update_fields=["chapter_count"])

        return chapters

    def _create_single_chapter(self, branch: Branch, chapter_number: int) -> Chapter:
        """Create a single chapter for a branch.

        Args:
            branch: Branch to create chapter for
            chapter_number: Chapter number within the branch

        Returns:
            Created chapter
        """
        status = KoreanDataGenerator.weighted_choice(
            list(ChapterStatus.choices),
            [0.3, 0.1, 0.6],  # DRAFT 30%, SCHEDULED 10%, PUBLISHED 60%
        )[0]
        access_type = KoreanDataGenerator.weighted_choice(
            list(AccessType.choices),
            [0.7, 0.3],  # FREE 70%, SUBSCRIPTION 30%
        )[0]

        title = KoreanDataGenerator.random_choice(KoreanDataGenerator.CHAPTER_TITLES)
        content_template = KoreanDataGenerator.random_choice(KoreanDataGenerator.CHAPTER_CONTENTS)
        content = content_template.format(title=title)

        chapter = Chapter(
            branch=branch,
            chapter_number=chapter_number,
            title=title,
            content=content,
            content_html=f"<p>{title}</p>",  # Simplified HTML
            word_count=len(content),
            status=status,
            access_type=access_type,
            price=KoreanDataGenerator.random_int(0, 300)
            if access_type == AccessType.FREE
            else KoreanDataGenerator.random_int(100, 500),
            scheduled_at=timezone.now() + timedelta(days=random.randint(1, 30))
            if status == ChapterStatus.SCHEDULED
            else None,
            published_at=timezone.now() - timedelta(days=random.randint(1, 365))
            if status == ChapterStatus.PUBLISHED
            else None,
            view_count=KoreanDataGenerator.random_int(0, 10000),
            like_count=KoreanDataGenerator.random_int(0, 500),
            comment_count=KoreanDataGenerator.random_int(0, 100),
        )
        chapter.save()

        return chapter

    # =========================================================================
    # Wiki Creation
    # =========================================================================

    def _create_wiki_entries(
        self, branches: list[Branch], count: int, chapters: list[Chapter]
    ) -> list[WikiEntry]:
        """Create wiki entries with snapshots."""
        wiki_entries = []

        # Create wiki tag definitions
        for branch in branches:
            if (
                KoreanDataGenerator.random_bool()
                and WikiTagDefinition.objects.filter(branch=branch).count() < 5
            ):
                for i in range(3):
                    tag_name = (
                        KoreanDataGenerator.random_choice(KoreanDataGenerator.TAG_NAMES)
                        + f" {i + 1}"
                    )
                    # Use get_or_create to handle unique constraint
                    tag, created = WikiTagDefinition.objects.get_or_create(
                        branch=branch,
                        name=tag_name,
                        defaults={
                            "color": f"#{random.randint(0, 0xFFFFFF):06x}",
                            "icon": "tag",
                            "description": f"태그 설명 {i + 1}",
                            "display_order": i,
                        },
                    )

        for i in range(count):
            branch = KoreanDataGenerator.random_choice(branches)
            branch_chapters = [c for c in chapters if c.branch_id == branch.id]

            # Check for empty chapters list
            if not branch_chapters:
                continue

            chapter = KoreanDataGenerator.random_choice(branch_chapters)

            wiki_entry_name = (
                KoreanDataGenerator.random_choice(KoreanDataGenerator.WIKI_ENTRY_NAMES)
                + f" {i + 1}"
            )
            # Use get_or_create to handle unique constraint
            wiki_entry, created = WikiEntry.objects.get_or_create(
                branch=branch,
                source_wiki=None,
                name=wiki_entry_name,
                defaults={
                    "image_url": f"https://example.com/wiki/{i + 1}.jpg",
                    "first_appearance": chapter.chapter_number,
                    "hidden_note": f"작성자 노트: 비공개 정보 {i + 1}",
                    "ai_metadata": {"confidence": random.random(), "tags": ["auto"]},
                },
            )
            if created:
                # Add tags
                tags = WikiTagDefinition.objects.filter(branch=branch)
                if tags:
                    wiki_entry.tags.add(KoreanDataGenerator.random_choice(tags))

                # Create snapshot
                snapshot = WikiSnapshot(
                    wiki_entry=wiki_entry,
                    content=f"위키 내용: {wiki_entry.name}에 대한 상세 설명입니다.\n\n이 항목은 회차 {chapter.chapter_number}부터 유효합니다.",
                    valid_from_chapter=chapter.chapter_number,
                    contributor_type=KoreanDataGenerator.random_choice(
                        list(ContributorType.choices)
                    )[0],
                    contributor=branch.author if random.random() > 0.3 else None,
                )
                snapshot.save()

                wiki_entries.append(wiki_entry)

        return wiki_entries

    # =========================================================================
    # Map Creation
    # =========================================================================

    def _create_maps(
        self, branches: list[Branch], count: int, chapters: list[Chapter]
    ) -> list[Map]:
        """Create maps with layers and objects."""
        maps = []

        for i in range(count):
            branch = KoreanDataGenerator.random_choice(branches)
            chapter = KoreanDataGenerator.random_choice(chapters)

            map_name = (
                KoreanDataGenerator.random_choice(KoreanDataGenerator.MAP_NAMES) + f" {i + 1}"
            )

            # Use get_or_create to handle unique constraint
            map_obj, map_created = Map.objects.get_or_create(
                branch=branch,
                name=map_name,
                defaults={
                    "source_map": None,
                    "description": f"{map_name}의 상세 설명입니다.",
                    "width": KoreanDataGenerator.random_int(800, 1920),
                    "height": KoreanDataGenerator.random_int(600, 1080),
                },
            )

            # Create or get snapshot
            if map_created:
                # Create new snapshot for newly created map
                snapshot = MapSnapshot(
                    map=map_obj,
                    valid_from_chapter=chapter.chapter_number,
                    base_image_url=f"https://example.com/maps/{i + 1}.jpg",
                )
                snapshot.save()
            else:
                # Get existing snapshot for existing map
                snapshot = MapSnapshot.objects.filter(map=map_obj).first()

            # Create layers and objects only if map was newly created
            if map_created:
                num_layers = KoreanDataGenerator.random_int(1, 5)
                for layer_idx in range(num_layers):
                    layer = MapLayer(
                        snapshot=snapshot,
                        name=f"레이어 {layer_idx + 1}",
                        layer_type=KoreanDataGenerator.random_choice(list(LayerType.choices))[0],
                        z_index=layer_idx,
                        is_visible=KoreanDataGenerator.random_bool(),
                        style_json={"opacity": random.random(), "blend_mode": "normal"},
                    )
                    layer.save()

                    # Create map objects
                    num_map_objects = KoreanDataGenerator.random_int(1, 10)
                    for obj_idx in range(num_map_objects):
                        map_object = MapObject(
                            layer=layer,
                            object_type=KoreanDataGenerator.random_choice(list(ObjectType.choices))[
                                0
                            ],
                            coordinates={
                                "x": random.randint(0, map_obj.width),
                                "y": random.randint(0, map_obj.height),
                            },
                            label=f"오브젝트 {obj_idx + 1}",
                            description=f"오브젝트 {obj_idx + 1}의 설명입니다.",
                            wiki_entry=None,  # Could link to wiki entries
                            style_json={
                                "color": f"#{random.randint(0, 0xFFFFFF):06x}",
                                "size": random.randint(5, 20),
                            },
                        )
                        map_object.save()

            # Only append to maps if it was newly created
            if map_created:
                maps.append(map_obj)

        return maps

    # =========================================================================
    # Interaction Creation
    # =========================================================================

    def _create_interactions(
        self, users: list[User], chapters: list[Chapter], branches: list[Branch]
    ) -> dict[str, int]:
        """Create various interactions."""
        stats = {}

        # Subscriptions
        subscriptions = []
        num_subscriptions = 20
        for _ in range(num_subscriptions):
            user = KoreanDataGenerator.random_choice(users)
            plan_type = KoreanDataGenerator.random_choice(list(PlanType.choices))[0]
            status = KoreanDataGenerator.random_choice(list(SubscriptionStatus.choices))[0]

            subscription, created = Subscription.objects.get_or_create(
                user=user,
                plan_type=plan_type,
                defaults={
                    "expires_at": timezone.now() + timedelta(days=random.randint(30, 365)),
                    "payment_id": f"PAY_{random.randint(100000, 999999)}",
                    "auto_renew": KoreanDataGenerator.random_bool(),
                    "status": status,
                    "cancelled_at": timezone.now() - timedelta(days=random.randint(1, 30))
                    if status != SubscriptionStatus.ACTIVE
                    else None,
                },
            )
            if created:
                subscriptions.append(subscription)
        stats["subscriptions"] = len(subscriptions)

        # Purchases
        purchases = []
        num_purchases = 50
        for _ in range(num_purchases):
            user = KoreanDataGenerator.random_choice(users)
            chapter = KoreanDataGenerator.random_choice(chapters)

            # Use get_or_create to handle unique constraint
            purchase, created = Purchase.objects.get_or_create(
                user=user,
                chapter=chapter,
                defaults={"price_paid": chapter.price},
            )
            if created:
                purchases.append(purchase)
        stats["purchases"] = len(purchases)

        # Reading logs
        reading_logs = []
        num_reading_logs = 100
        for _ in range(num_reading_logs):
            user = KoreanDataGenerator.random_choice(users)
            chapter = KoreanDataGenerator.random_choice(chapters)

            # Use get_or_create to handle unique constraint
            log, created = ReadingLog.objects.get_or_create(
                user=user,
                chapter=chapter,
                defaults={
                    "progress": random.random(),
                    "is_completed": KoreanDataGenerator.random_bool(),
                    "read_at": timezone.now() - timedelta(days=random.randint(0, 365)),
                },
            )
            if created:
                reading_logs.append(log)
        stats["reading_logs"] = len(reading_logs)

        # Bookmarks
        bookmarks = []
        num_bookmarks = 30
        for _ in range(num_bookmarks):
            user = KoreanDataGenerator.random_choice(users)
            chapter = KoreanDataGenerator.random_choice(chapters)

            # Use get_or_create to handle unique constraint
            bookmark, created = Bookmark.objects.get_or_create(
                user=user,
                chapter=chapter,
                defaults={
                    "scroll_position": random.random(),
                    "note": KoreanDataGenerator.random_choice(
                        ["재밌는 부분", "중요한 장면", "다시 읽어야 함", ""]
                    ),
                },
            )
            if created:
                bookmarks.append(bookmark)
        stats["bookmarks"] = len(bookmarks)

        # Comments
        comments = []
        num_comments = 100

        for _ in range(num_comments):
            user = KoreanDataGenerator.random_choice(users)
            chapter = KoreanDataGenerator.random_choice(chapters)

            comment = Comment(
                user=user,
                chapter=chapter,
                parent=None,  # Top-level comments only for simplicity
                content=KoreanDataGenerator.random_choice(KoreanDataGenerator.COMMENT_CONTENTS),
                is_spoiler=KoreanDataGenerator.random_bool(),
                is_pinned=False,
                like_count=KoreanDataGenerator.random_int(0, 100),
                paragraph_index=KoreanDataGenerator.random_int(0, 10)
                if KoreanDataGenerator.random_bool()
                else None,
                selection_start=KoreanDataGenerator.random_int(0, 500)
                if KoreanDataGenerator.random_bool()
                else None,
                selection_end=KoreanDataGenerator.random_int(0, 500)
                if KoreanDataGenerator.random_bool()
                else None,
                quoted_text=KoreanDataGenerator.random_choice(KoreanDataGenerator.COMMENT_CONTENTS)[
                    :50
                ]
                if KoreanDataGenerator.random_bool()
                else "",
            )
            # Fix selection_end > selection_start if both set
            if comment.selection_start is not None and comment.selection_end is not None:
                if comment.selection_start >= comment.selection_end:
                    comment.selection_end = comment.selection_start + 10
            comment.save()
            comments.append(comment)
        stats["comments"] = len(comments)

        # Likes (on chapters and comments)
        likes = []
        num_likes = 100

        # Chapter content type
        chapter_ct = ContentType.objects.get_for_model(Chapter)
        comment_ct = ContentType.objects.get_for_model(Comment)

        for _ in range(num_likes):
            user = KoreanDataGenerator.random_choice(users)
            is_chapter_like = KoreanDataGenerator.random_bool()

            if is_chapter_like:
                content_type = chapter_ct
                obj = KoreanDataGenerator.random_choice(chapters)
            else:
                content_type = comment_ct
                obj = KoreanDataGenerator.random_choice(comments)

            # User cannot like own content
            if obj.author.id == user.id:
                continue

            # Use get_or_create to handle unique constraint
            like, created = Like.objects.get_or_create(
                user=user, content_type=content_type, object_id=obj.id
            )
            if created:
                likes.append(like)
        stats["likes"] = len(likes)

        # Reports
        reports = []
        num_reports = 10
        for _ in range(num_reports):
            reporter = KoreanDataGenerator.random_choice(users)
            is_comment_report = KoreanDataGenerator.random_bool()

            if is_comment_report:
                content_type = comment_ct
                obj = KoreanDataGenerator.random_choice(comments)
            else:
                content_type = chapter_ct
                obj = KoreanDataGenerator.random_choice(chapters)

            # Use get_or_create to handle unique constraint
            status = KoreanDataGenerator.random_choice(list(ReportStatus.choices))[0]
            report, created = Report.objects.get_or_create(
                reporter=reporter,
                content_type=content_type,
                object_id=obj.id,
                defaults={
                    "reason": KoreanDataGenerator.random_choice(list(ReportReason.choices))[0],
                    "description": KoreanDataGenerator.random_choice(
                        KoreanDataGenerator.REPORT_DESCRIPTIONS
                    ),
                    "status": status,
                    "resolver": KoreanDataGenerator.random_choice(users)
                    if status != ReportStatus.PENDING
                    else None,
                    "resolved_at": timezone.now() - timedelta(days=random.randint(1, 30))
                    if status != ReportStatus.PENDING
                    else None,
                    "resolution_note": "처리 완료"
                    if status == ReportStatus.RESOLVED
                    else "부적절한 신고로 반려"
                    if status == ReportStatus.REJECTED
                    else "",
                },
            )
            if created:
                reports.append(report)
        stats["reports"] = len(reports)

        return stats

    # =========================================================================
    # Wallet and Transaction Creation
    # =========================================================================

    def _create_wallets_and_transactions(self, users: list[User]) -> dict[str, int]:
        """Create wallets and coin transactions for users."""
        stats = {}

        wallets = []
        transactions_created = []
        for user in users:
            balance = user.coin
            # Use get_or_create to handle OneToOne constraint
            wallet, created = Wallet.objects.get_or_create(user=user, defaults={"balance": balance})
            if created:
                wallets.append(wallet)

                # Create transactions only for newly created wallets
                num_transactions = KoreanDataGenerator.random_int(5, 20)
                current_balance = 0

                for _ in range(num_transactions):
                    transaction_type = KoreanDataGenerator.random_choice(
                        list(TransactionType.choices)
                    )[0]
                    amount = KoreanDataGenerator.random_int(100, 5000)

                    if transaction_type == TransactionType.SPEND:
                        amount = -amount

                    current_balance += amount
                    if current_balance < 0:
                        current_balance = 0
                        continue

                    # Update wallet balance after each transaction
                    current_balance = max(current_balance, 0)

                    transaction = CoinTransaction(
                        wallet=wallet,
                        transaction_type=transaction_type,
                        amount=amount,
                        balance_after=current_balance,
                        description=KoreanDataGenerator.random_choice(
                            KoreanDataGenerator.TRANSACTION_DESCRIPTIONS
                        ),
                        reference_type="chapter"
                        if transaction_type == TransactionType.SPEND
                        else "charge",
                        reference_id=KoreanDataGenerator.random_int(1, 100),
                    )
                    transaction.save()
                    transactions_created.append(transaction)

        stats["wallets"] = len(wallets)
        stats["coin_transactions"] = len(transactions_created)

        return stats

    # =========================================================================
    # AI Usage Log Creation
    # =========================================================================

    def _create_ai_usage_logs(self, users: list[User], count: int) -> list[AIUsageLog]:
        """Create AI usage logs."""
        ai_logs = []

        for _ in range(count):
            user = KoreanDataGenerator.random_choice(users)
            action_type = KoreanDataGenerator.random_choice(list(AIActionType.choices))[0]
            usage_date = timezone.now().date() - timedelta(days=random.randint(0, 30))

            # Use get_or_create to handle unique constraint
            ai_log, created = AIUsageLog.objects.get_or_create(
                user=user,
                usage_date=usage_date,
                action_type=action_type,
                defaults={
                    "request_count": KoreanDataGenerator.random_int(1, 10),
                    "token_count": KoreanDataGenerator.random_int(100, 5000),
                },
            )
            if created:
                ai_logs.append(ai_log)

        return ai_logs

    # =========================================================================
    # Summary Printing
    # =========================================================================

    def _print_summary(self, stats: dict[str, int]) -> None:
        """Print summary statistics."""
        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("SEEDING COMPLETE"))
        self.stdout.write(self.style.SUCCESS("=" * 60))

        categories = {
            "Users": ["users"],
            "Novels & Branches": ["novels", "main_branches", "side_branches"],
            "Contents": ["chapters", "wiki_entries", "maps"],
            "Interactions": [
                "subscriptions",
                "purchases",
                "reading_logs",
                "bookmarks",
                "comments",
                "likes",
                "reports",
            ],
            "Wallet & AI": ["wallets", "coin_transactions", "ai_usage_logs"],
        }

        for category, keys in categories.items():
            self.stdout.write(f"\n{category}:")
            for key in keys:
                if key in stats:
                    self.stdout.write(f"  {key}: {stats[key]}")

        total = sum(stats.values())
        self.stdout.write(f"\nTotal records created: {total}")
        self.stdout.write(self.style.SUCCESS("=" * 60))
