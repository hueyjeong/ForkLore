package io.forklore.dto.request;

import io.forklore.domain.chapter.AccessType;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Size;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
@Schema(description = "회차 수정 요청")
public class ChapterUpdateRequest {

    @Size(max = 200, message = "제목은 200자 이하여야 합니다")
    @Schema(description = "회차 제목")
    private String title;

    @Schema(description = "본문 (마크다운)")
    private String content;

    @Schema(description = "접근 타입")
    private AccessType accessType;

    @Schema(description = "가격")
    private Integer price;

    @Size(max = 2000, message = "작가의 말은 2000자 이하여야 합니다")
    @Schema(description = "작가의 말")
    private String authorComment;

    @Builder
    public ChapterUpdateRequest(String title, String content, AccessType accessType,
            Integer price, String authorComment) {
        this.title = title;
        this.content = content;
        this.accessType = accessType;
        this.price = price;
        this.authorComment = authorComment;
    }
}
