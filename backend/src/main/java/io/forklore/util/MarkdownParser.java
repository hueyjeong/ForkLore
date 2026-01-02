package io.forklore.util;

import com.vladsch.flexmark.html.HtmlRenderer;
import com.vladsch.flexmark.parser.Parser;
import com.vladsch.flexmark.util.ast.Node;
import com.vladsch.flexmark.util.data.MutableDataSet;
import org.owasp.encoder.Encode;
import org.springframework.stereotype.Component;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * 마크다운 → HTML 변환 유틸리티
 * - Flexmark 라이브러리 사용
 * - XSS 방지를 위한 HTML 인코딩
 * - 위키 키워드 자동 링크 지원
 */
@Component
public class MarkdownParser {

    private final Parser parser;
    private final HtmlRenderer renderer;

    // 위키 키워드 패턴: [[Keyword]] 형식
    private static final Pattern WIKI_LINK_PATTERN = Pattern.compile("\\[\\[([^\\]]+)\\]\\]");

    public MarkdownParser() {
        MutableDataSet options = new MutableDataSet();
        this.parser = Parser.builder(options).build();
        this.renderer = HtmlRenderer.builder(options).build();
    }

    /**
     * 마크다운을 HTML로 변환
     * 
     * @param markdown 마크다운 텍스트
     * @return HTML 문자열
     */
    public String toHtml(String markdown) {
        if (markdown == null || markdown.isEmpty()) {
            return "";
        }

        // 1. 위키 링크 변환
        String processed = processWikiLinks(markdown);

        // 2. 마크다운 → HTML 변환
        Node document = parser.parse(processed);
        String html = renderer.render(document);

        return html;
    }

    /**
     * 위키 키워드 [[Keyword]] → <a class="wiki-link" href="/wiki/Keyword">Keyword</a>
     */
    private String processWikiLinks(String text) {
        Matcher matcher = WIKI_LINK_PATTERN.matcher(text);
        StringBuilder result = new StringBuilder();

        while (matcher.find()) {
            String keyword = matcher.group(1);
            String safeKeyword = Encode.forHtml(keyword);
            String link = String.format("<a class=\"wiki-link\" data-wiki=\"%s\">%s</a>",
                    safeKeyword, safeKeyword);
            matcher.appendReplacement(result, Matcher.quoteReplacement(link));
        }
        matcher.appendTail(result);

        return result.toString();
    }

    /**
     * 마크다운 텍스트의 단어 수 계산
     */
    public int countWords(String markdown) {
        if (markdown == null || markdown.isEmpty()) {
            return 0;
        }
        // HTML 태그 및 마크다운 문법 제거 후 단어 수 계산
        String plainText = markdown
                .replaceAll("\\[\\[[^\\]]+\\]\\]", " ") // 위키 링크 제거
                .replaceAll("[#*_`\\[\\]()>-]", " ") // 마크다운 문법 제거
                .replaceAll("\\s+", " ") // 연속 공백 정리
                .trim();

        if (plainText.isEmpty()) {
            return 0;
        }

        // 한글/영어 혼합 단어 수 계산
        return plainText.split("\\s+").length;
    }
}
