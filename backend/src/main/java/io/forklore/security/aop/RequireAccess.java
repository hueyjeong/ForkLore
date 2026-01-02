package io.forklore.security.aop;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * 회차 열람 권한 검사 어노테이션
 * 
 * 컨트롤러 메서드에 이 어노테이션을 붙이면 회차 접근 권한을 자동으로 검사합니다.
 * 
 * 사용 예:
 * 
 * <pre>
 * {@code @RequireAccess}
 * public ApiResponse<ChapterResponse> getChapter(
 *     @PathVariable Long chapterId, ...
 * ) { ... }
 * </pre>
 */
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface RequireAccess {

    /**
     * 회차 ID를 담고 있는 파라미터 이름
     * 기본값: "chapterId"
     */
    String chapterIdParam() default "chapterId";

    /**
     * 권한이 없을 때 예외를 던질지, false를 반환할지 결정
     * 기본값: true (예외 발생)
     */
    boolean throwOnDenied() default true;
}
