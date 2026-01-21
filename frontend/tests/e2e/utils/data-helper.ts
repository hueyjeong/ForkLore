/**
 * 테스트 데이터를 재설정하도록 예약된 함수지만 현재 구현되어 있지 않습니다.
 *
 * 현재 호출하면 테스트 격리가 보장되지 않음을 알리는 오류를 던집니다.
 *
 * @throws `Error` - 'resetTestData not implemented - test isolation not guaranteed' 메시지를 가진 오류
 */
export async function resetTestData() {
  throw new Error('resetTestData not implemented - test isolation not guaranteed');
}