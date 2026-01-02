---
name: 🎨 프론트엔드 기능 개발
about: 프론트엔드 신규 기능 개발 또는 개선을 위한 이슈
title: '[FE] '
labels: ['frontend', 'feature']
assignees: ''
---

## 📋 작업 개요
<!-- 개발할 기능에 대한 간단한 설명 -->

## 🎯 목표
<!-- 이 작업을 통해 달성하려는 목표 -->

## 📌 우선순위
- [ ] P0 (MVP 필수)
- [ ] P1 (MVP 권장)
- [ ] P2 (후속)

## 🔧 난이도 및 예상 공수
- **난이도**: 
  - [ ] 🟢 Easy
  - [ ] 🟡 Medium
  - [ ] 🔴 Hard
- **예상 공수**: ___h

## 🎨 디자인 상세

### 페이지/컴포넌트 구조
<!-- 구현할 페이지나 컴포넌트 구조 -->
```
app/
  └── (route)/
      └── page.tsx
components/
  └── feature/
      └── Component.tsx
```

### UI/UX 요구사항
<!-- 디자인 요구사항 및 사용자 경험 시나리오 -->

### 반응형 고려사항
- [ ] 모바일 (< 768px)
- [ ] 태블릿 (768px - 1024px)
- [ ] 데스크톱 (> 1024px)

## 🔌 API 연동
<!-- 연동할 백엔드 API -->
- `GET /api/v1/...`
- `POST /api/v1/...`

## 🗂️ 상태 관리
<!-- Zustand 스토어 또는 TanStack Query 사용 계획 -->

### 서버 상태 (TanStack Query)
```typescript
// 예시
const useExample = () => {
  return useQuery({
    queryKey: ['example'],
    queryFn: fetchExample,
  });
};
```

### 클라이언트 상태 (Zustand)
```typescript
// 예시
interface ExampleStore {
  // ...
}
```

## 📦 필요한 라이브러리
<!-- 추가로 설치해야 할 라이브러리가 있다면 -->
- [ ] 라이브러리명 (버전)

## ✅ 테스트 체크리스트
- [ ] 컴포넌트 단위 테스트 (Vitest)
- [ ] E2E 테스트 (Playwright) - 필요 시
- [ ] 접근성 테스트 (a11y)
- [ ] 반응형 테스트

## 🔗 관련 문서
<!-- 관련 문서 링크 -->
- `docs/frontend-tasks.md` - Line: 
- `docs/design-system.md`
- Figma 링크: 

## 🎨 디자인 시스템 준수
- [ ] shadcn/ui 컴포넌트 활용
- [ ] Tailwind CSS 4.x 스타일 가이드 준수
- [ ] OKLCH 색상 시스템 사용
- [ ] Lucide Icons 사용
- [ ] Geist 폰트 사용

## 📝 참고 사항
<!-- 추가 참고 사항이나 주의점 -->

## ✅ 완료 조건 (Definition of Done)
- [ ] 컴포넌트 구현 완료
- [ ] 디자인 시스템 준수
- [ ] 반응형 구현 완료
- [ ] 테스트 작성 및 통과
- [ ] 코드 리뷰 완료
- [ ] 접근성 검증 완료
- [ ] 브라우저 호환성 확인
