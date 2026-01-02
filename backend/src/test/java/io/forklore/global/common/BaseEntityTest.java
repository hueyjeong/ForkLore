package io.forklore.global.common;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
@Transactional
class BaseEntityTest {

    @Autowired
    private TestEntityRepository testEntityRepository;

    @Test
    @DisplayName("BaseEntity를 상속받은 엔티티 저장 시 생성/수정 시간이 자동 저장된다")
    void auditing_test() {
        // given
        TestEntity testEntity = new TestEntity("test");

        // when
        TestEntity savedEntity = testEntityRepository.save(testEntity);

        // then
        assertThat(savedEntity.getCreatedAt()).isNotNull();
        assertThat(savedEntity.getUpdatedAt()).isNotNull();
        assertThat(savedEntity.getCreatedAt()).isBeforeOrEqualTo(LocalDateTime.now());
    }
}
