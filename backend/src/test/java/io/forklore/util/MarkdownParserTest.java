package io.forklore.util;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

class MarkdownParserTest {

    private MarkdownParser markdownParser;

    @BeforeEach
    void setUp() {
        markdownParser = new MarkdownParser();
    }

    @Test
    @DisplayName("헤더 변환")
    void convertHeader() {
        // given
        String markdown = "# 제목1\n## 제목2\n### 제목3";

        // when
        String html = markdownParser.toHtml(markdown);

        // then
        assertThat(html).contains("<h1>제목1</h1>");
        assertThat(html).contains("<h2>제목2</h2>");
        assertThat(html).contains("<h3>제목3</h3>");
    }

    @Test
    @DisplayName("강조 텍스트 변환")
    void convertEmphasis() {
        // given
        String markdown = "**굵게** *기울임*";

        // when
        String html = markdownParser.toHtml(markdown);

        // then
        assertThat(html).contains("<strong>굵게</strong>");
        assertThat(html).contains("<em>기울임</em>");
    }

    @Test
    @DisplayName("리스트 변환")
    void convertList() {
        // given
        String markdown = "- 항목1\n- 항목2\n- 항목3";

        // when
        String html = markdownParser.toHtml(markdown);

        // then
        assertThat(html).contains("<ul>");
        assertThat(html).contains("<li>항목1</li>");
        assertThat(html).contains("</ul>");
    }

    @Test
    @DisplayName("위키 링크 변환")
    void convertWikiLink() {
        // given
        String markdown = "이것은 [[마법검]]에 대한 이야기입니다.";

        // when
        String html = markdownParser.toHtml(markdown);

        // then
        assertThat(html).contains("class=\"wiki-link\"");
        assertThat(html).contains("data-wiki=\"마법검\"");
        assertThat(html).contains(">마법검</a>");
    }

    @Test
    @DisplayName("복합 위키 링크 변환")
    void convertMultipleWikiLinks() {
        // given
        String markdown = "[[용사]]가 [[마왕]]을 물리쳤다.";

        // when
        String html = markdownParser.toHtml(markdown);

        // then
        assertThat(html).contains("data-wiki=\"용사\"");
        assertThat(html).contains("data-wiki=\"마왕\"");
    }

    @Test
    @DisplayName("단어 수 계산")
    void countWords() {
        // given
        String markdown = "안녕하세요 세계. Hello World.";

        // when
        int count = markdownParser.countWords(markdown);

        // then
        assertThat(count).isEqualTo(4); // "안녕하세요", "세계.", "Hello", "World."
    }

    @Test
    @DisplayName("빈 문자열 처리")
    void handleEmptyString() {
        // when
        String html = markdownParser.toHtml("");
        int count = markdownParser.countWords(null);

        // then
        assertThat(html).isEmpty();
        assertThat(count).isZero();
    }

    @Test
    @DisplayName("XSS 위키 키워드 방지")
    void preventXssInWikiKeyword() {
        // given
        String markdown = "[[<script>alert('xss')</script>]]";

        // when
        String html = markdownParser.toHtml(markdown);

        // then
        assertThat(html).doesNotContain("<script>");
        assertThat(html).contains("&lt;script&gt;");
    }
}
