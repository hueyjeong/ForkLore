"""
API 문서 태그 테스트
novels 앱의 각 ViewSet이 올바른 OpenAPI 태그를 가지고 있는지 확인
"""

from django.test import TestCase
from drf_spectacular.generators import SchemaGenerator


class TestNovelViewSetTags(TestCase):
    """NovelViewSet의 스키마 태그 테스트"""

    def test_novel_viewset_has_novels_tag(self):
        """NovelViewSet의 모든 엔드포인트가 'Novels' 태그를 가져야 함"""
        generator = SchemaGenerator()
        schema = generator.get_schema()

        # NovelViewSet 경로들 (브랜치가 아닌 novels 직접 엔드포인트)
        novel_endpoints_found = False

        for path, methods in schema["paths"].items():
            # /api/v1/novels/ 경로이면서 브랜치가 아닌 것만
            if "/novels/" in path and "/branches" not in path:
                novel_endpoints_found = True
                for method, operation in methods.items():
                    if method != "parameters":
                        tags = operation.get("tags", [])
                        self.assertIn(
                            "Novels",
                            tags,
                            f"Expected 'Novels' tag in {method.upper()} {path}, got {tags}",
                        )

        self.assertTrue(novel_endpoints_found, "No novel endpoints found in schema")


class TestBranchViewSetTags(TestCase):
    """BranchViewSet의 스키마 태그 테스트"""

    def test_branch_viewset_has_branches_tag(self):
        """BranchViewSet의 모든 엔드포인트가 'Branches' 태그를 가져야 함"""
        generator = SchemaGenerator()
        schema = generator.get_schema()

        # BranchViewSet는 NovelViewSet 아래 nested되어 있음
        # /api/v1/novels/{novel_pk}/branches/ 형태
        branch_endpoints_found = False

        for path, methods in schema["paths"].items():
            # nested branch 경로 찾기
            if "/novels/" in path and "/branches/" in path:
                # link-requests는 제외 (별도 ViewSet)
                if "/link-requests" in path:
                    continue

                branch_endpoints_found = True
                for method, operation in methods.items():
                    if method != "parameters":
                        tags = operation.get("tags", [])
                        # main action과 link_request action은 별도 태그를 가질 수 있음
                        # 하지만 대부분은 Branches 태그여야 함
                        if "Branch Links" not in tags:
                            self.assertIn(
                                "Branches",
                                tags,
                                f"Expected 'Branches' tag in {method.upper()} {path}, got {tags}",
                            )

        self.assertTrue(branch_endpoints_found, "No branch endpoints found in schema")


class TestBranchDetailViewSetTags(TestCase):
    """BranchDetailViewSet의 스키마 태그 테스트"""

    def test_branch_detail_viewset_has_branches_tag(self):
        """BranchDetailViewSet의 엔드포인트가 적절한 태그를 가져야 함"""
        generator = SchemaGenerator()
        schema = generator.get_schema()

        # BranchDetailViewSet 엔드포인트들
        # /api/v1/branches/{id}/ 형태
        branch_detail_found = False

        for path, methods in schema["paths"].items():
            # 독립적인 branch 상세 경로 찾기
            if "/branches/{id}" in path:
                branch_detail_found = True
                for method, operation in methods.items():
                    if method != "parameters":
                        tags = operation.get("tags", [])
                        # link-request 액션은 "Branch Links" 태그
                        if "link-request" in path:
                            self.assertIn(
                                "Branch Links",
                                tags,
                                f"Expected 'Branch Links' tag in {method.upper()} {path}, got {tags}",
                            )
                        else:
                            # 나머지는 모두 "Branches" 태그
                            self.assertIn(
                                "Branches",
                                tags,
                                f"Expected 'Branches' tag in {method.upper()} {path}, got {tags}",
                            )

        self.assertTrue(branch_detail_found, "No branch detail endpoints found in schema")
