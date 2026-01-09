package io.forklore.global.error;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.junit.jupiter.api.BeforeEach;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@ActiveProfiles("test")
class GlobalExceptionHandlerTest {

    private MockMvc mockMvc;

    @BeforeEach
    void setUp() {
        mockMvc = MockMvcBuilders.standaloneSetup(new TestController())
                .setControllerAdvice(new GlobalExceptionHandler())
                .build();
    }

    @RestController
    static class TestController {
        @GetMapping("/test/business-exception")
        public void throwBusinessException() {
            throw new BusinessException(CommonErrorCode.ENTITY_NOT_FOUND);
        }
    }

    @Test
    @DisplayName("BusinessException 발생 시 표준 에러 응답 포맷을 반환한다")
    void businessException_response_test() throws Exception {
        mockMvc.perform(get("/test/business-exception")
                .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.message").value(CommonErrorCode.ENTITY_NOT_FOUND.getMessage()))
                .andExpect(jsonPath("$.status").value(CommonErrorCode.ENTITY_NOT_FOUND.getStatus().value()))
                .andExpect(jsonPath("$.code").value(CommonErrorCode.ENTITY_NOT_FOUND.getCode()));
    }
}
