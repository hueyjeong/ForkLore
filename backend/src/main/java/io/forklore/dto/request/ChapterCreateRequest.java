package io.forklore.dto.request;

import io.forklore.domain.chapter.AccessType;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
@Schema(description = "회차 생성 요청")
public class ChapterCreateRequest {

    @NotBlank(message = "제목은 필수입니다")
    @Size(max = 200, message = "제목은 200자 이하여야 합니다")
    @Schema(description = "회차 제목", example = "1화. 시작")
    private String title;

    @NotBlank(message = "본문은 필수입니다")
    @Schema(description = "본문 (마크다운)")
    private String content;

    @Schema(description = "접근 타입", example = "FREE")
    private AccessType accessType;

    @Schema(description = "가격 (구독 타입일 때)", example = "0")
    private Integer price;

    @Size(max = 2000, message = "작가의 말은 2000자 이하여야 합니다")
    @Schema(description = "작가의 말")
    private String authorComment;

    @Builder
    public ChapterCreateRequest(String title, String content, AccessType accessType,
            Integer price, String authorComment) {
        this.title = title;
        this.content = content;
        this.accessType = accessType;
        this.price = price;
        this.authorComment = authorComment;
    }
}
