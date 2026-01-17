# ⚛️ React 19 가이드

**작성일**: 2026.01.16  
**작성자**: Antigravity  
**문서 버전**: v1.0

---

> ForkLore 프로젝트를 위한 React 19 신규 기능 및 패턴 가이드

## 1. 개요 (Overview)
React 19는 비동기 데이터 로딩, 폼 처리, 그리고 서버와의 상호작용을 더욱 단순화하고 직관적으로 개선했습니다. 특히 **Actions API**와 **Server Components**의 정식 지원을 통해 클라이언트와 서버 간의 경계를 허물고, 사용자 경험을 극대화하는 동시에 개발자 생산성을 높이는 데 집중합니다.

## 2. 새로운 훅 (New Hooks)

### 2.1 `use()`
`use()`는 렌더링 도중 Promise나 Context를 읽을 수 있게 해주는 새로운 API입니다. 조건문이나 반복문 안에서도 호출할 수 있다는 점이 특징입니다.

```tsx
import { use } from 'react';

function NovelContent({ contentPromise }) {
  // Promise가 resolve될 때까지 기다림 (Suspense와 함께 사용)
  const content = use(contentPromise);
  return <div>{content}</div>;
}

function ThemeWrapper({ children }) {
  // Context도 use()로 읽기 가능
  const theme = use(ThemeContext);
  return <div className={theme}>{children}</div>;
}
```

### 2.2 `useOptimistic()`
서버 응답을 기다리지 않고 UI를 즉시 업데이트하는 '낙관적 업데이트'를 쉽게 구현할 수 있습니다.

```tsx
import { useOptimistic } from 'react';

function CommentList({ comments, addCommentAction }) {
  const [optimisticComments, addOptimisticComment] = useOptimistic(
    comments,
    (state, newComment) => [...state, { text: newComment, sending: true }]
  );

  async function formAction(formData) {
    const text = formData.get("comment");
    addOptimisticComment(text);
    await addCommentAction(text);
  }
  // ...
}
```

### 2.3 `useFormStatus()`
부모 `<form>`의 상태(제출 여부 등)를 하위 컴포넌트에서 쉽게 가져올 수 있습니다.

```tsx
import { useFormStatus } from 'react-dom';

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <button disabled={pending}>
      {pending ? '저장 중...' : '저장'}
    </button>
  );
}
```

### 2.4 `useActionState()`
이전 `useFormState`의 발전된 형태로, 폼 액션의 결과와 펜딩 상태를 한 번에 관리합니다.

```tsx
import { useActionState } from 'react';

async function updateUsername(prevState, formData) {
  const result = await api.update(formData.get("name"));
  return result.error ? { error: result.error } : { success: true };
}

function ProfileForm() {
  const [state, formAction, isPending] = useActionState(updateUsername, { error: null });

  return (
    <form action={formAction}>
      <input name="name" />
      {state.error && <p>{state.error}</p>}
      <button disabled={isPending}>업데이트</button>
    </form>
  );
}
```

## 3. Server Components
React 19에서 RSC(React Server Components)는 핵심 아키텍처입니다.

- **장점**: 
    - 서버에서만 실행되어 번들 크기 감소.
    - 데이터베이스나 파일 시스템에 직접 접근 가능.
    - 보안 민감 정보(API 키 등)를 클라이언트에 노출하지 않음.
- **지시어**:
    - `'use server'`: 서버 액션을 정의할 때 사용.
    - `'use client'`: 상호작용(state, effects)이 필요한 클라이언트 경계를 정의할 때 사용.

## 4. Actions와 폼 처리
React 19는 HTML 폼을 현대적으로 재해석합니다.

- **Form Action**: `<form action={fn}>`을 통해 비동기 함수를 직접 전달합니다.
- **Server Actions**: 서버에서 실행되는 함수를 클라이언트에서 직접 호출하여 RPC(Remote Procedure Call)처럼 사용합니다.
- **Progressive Enhancement**: 자바스크립트가 로드되기 전에도 폼 제출이 가능하도록 설계되어 있습니다.

## 5. 동시성 기능 (Concurrent Features)
동시성 렌더링을 통해 대규모 업데이트 중에도 UI가 멈추지 않도록 합니다.

- **Suspense 개선**: 하이드레이션 순서 최적화 및 서버 사이드 렌더링과의 연동 강화.
- **Transitions**: `startTransition`을 사용하여 우선순위가 낮은 업데이트를 분리합니다. `useTransition`은 이제 비동기 함수를 지원합니다.
- **useDeferredValue**: 입력값에 따라 무거운 컴포넌트를 렌더링할 때, 최신 값의 업데이트를 지연시켜 성능을 확보합니다.

## 6. React 18에서 마이그레이션

### 6.1 주요 변경 사항 비교

| 기능 | React 18 (이전) | React 19 (권장) |
| :--- | :--- | :--- |
| **Ref 전달** | `forwardRef` 사용 필수 | **Ref를 일반 Prop으로 전달 가능** |
| **폼 상태 관리** | `useState` + `onSubmit` | `useActionState` + `action` |
| **Context 사용** | `useContext(Ctx)` | `use(Ctx)` (조건부 가능) |
| **메타데이터** | `react-helmet` 등 외부 라이브러리 | `<title>`, `<meta>` 직접 렌더링 지원 |

### 6.2 코드 변환 예시 (Before/After)

**Ref 전달 (Ref as a Prop)**
```tsx
// Before (React 18)
const MyInput = forwardRef((props, ref) => {
  return <input {...props} ref={ref} />;
});

// After (React 19)
function MyInput({ placeholder, ref }) {
  return <input placeholder={placeholder} ref={ref} />;
}
```

**Context 공급자 (Simplified Context Provider)**
```tsx
// Before (React 18)
<ThemeContext.Provider value="dark">{children}</ThemeContext.Provider>

// After (React 19)
<ThemeContext value="dark">{children}</ThemeContext>
```

---

## 문서 끝
