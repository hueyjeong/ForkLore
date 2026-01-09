package io.forklore.security.aop;

import io.forklore.global.error.ForbiddenException;
import io.forklore.security.UserPrincipal;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.reflect.MethodSignature;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;

import java.lang.reflect.Method;
import java.lang.reflect.Parameter;

/**
 * 회차 열람 권한 검사 AOP Aspect
 * 
 * @RequireAccess 어노테이션이 붙은 메서드 실행 전 권한 검사를 수행합니다.
 */
@Aspect
@Component
@RequiredArgsConstructor
@Slf4j
public class AccessCheckAspect {

    private final AccessChecker accessChecker;

    @Around("@annotation(requireAccess)")
    public Object checkAccess(ProceedingJoinPoint joinPoint, RequireAccess requireAccess) throws Throwable {
        String paramName = requireAccess.chapterIdParam();
        Long chapterId = extractChapterId(joinPoint, paramName);

        if (chapterId == null) {
            log.warn("회차 ID를 찾을 수 없음. 파라미터: {}", paramName);
            throw new IllegalArgumentException("회차 ID 파라미터를 찾을 수 없습니다: " + paramName);
        }

        Long userId = getCurrentUserId();

        boolean hasAccess = accessChecker.canAccessChapter(userId, chapterId);

        if (!hasAccess) {
            if (requireAccess.throwOnDenied()) {
                throw new ForbiddenException("이 회차에 대한 접근 권한이 없습니다. 구독 또는 개별 구매가 필요합니다.");
            }
            // throwOnDenied가 false면 null 리턴 (호출자가 처리)
            return null;
        }

        return joinPoint.proceed();
    }

    /**
     * 메서드 파라미터에서 회차 ID 추출
     */
    private Long extractChapterId(ProceedingJoinPoint joinPoint, String paramName) {
        MethodSignature signature = (MethodSignature) joinPoint.getSignature();
        Method method = signature.getMethod();
        Parameter[] parameters = method.getParameters();
        Object[] args = joinPoint.getArgs();

        for (int i = 0; i < parameters.length; i++) {
            // 파라미터 이름으로 매칭
            if (parameters[i].getName().equals(paramName)) {
                Object value = args[i];
                if (value instanceof Long) {
                    return (Long) value;
                } else if (value instanceof String) {
                    return Long.parseLong((String) value);
                } else if (value instanceof Integer) {
                    return ((Integer) value).longValue();
                }
            }

            // @PathVariable 또는 @RequestParam 이름 확인
            var pathVariable = parameters[i].getAnnotation(
                    org.springframework.web.bind.annotation.PathVariable.class);
            if (pathVariable != null) {
                String name = pathVariable.value().isEmpty()
                        ? pathVariable.name().isEmpty() ? parameters[i].getName() : pathVariable.name()
                        : pathVariable.value();
                if (name.equals(paramName) || parameters[i].getName().equals(paramName)) {
                    Object value = args[i];
                    if (value instanceof Long) {
                        return (Long) value;
                    }
                }
            }
        }

        // "id" 또는 "chapterId"로 끝나는 Long 파라미터 찾기 (fallback)
        for (int i = 0; i < parameters.length; i++) {
            if (parameters[i].getType() == Long.class &&
                    (parameters[i].getName().endsWith("Id") || parameters[i].getName().equals("id"))) {
                return (Long) args[i];
            }
        }

        return null;
    }

    /**
     * 현재 인증된 사용자 ID 조회
     */
    private Long getCurrentUserId() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();

        if (authentication == null || !authentication.isAuthenticated()) {
            return null;
        }

        Object principal = authentication.getPrincipal();
        if (principal instanceof UserPrincipal userPrincipal) {
            return userPrincipal.getId();
        }

        return null;
    }
}
