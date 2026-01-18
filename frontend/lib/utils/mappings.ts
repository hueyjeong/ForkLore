import { Genre, AgeRating, NovelStatus } from '@/types/novels.types';

export const GENRE_LABELS: Record<Genre, string> = {
  [Genre.FANTASY]: '판타지',
  [Genre.ROMANCE]: '로맨스',
  [Genre.ROMANCE_FANTASY]: '로판',
  [Genre.MODERN_FANTASY]: '현판',
  [Genre.WUXIA]: '무협',
  [Genre.MYSTERY]: '미스터리',
  [Genre.LIGHT_NOVEL]: '라이트노벨',
  [Genre.BL]: 'BL',
  [Genre.GL]: 'GL',
  [Genre.TS]: 'TS',
  [Genre.SPORTS]: '스포츠',
  [Genre.ALTERNATIVE_HISTORY]: '대체역사',
  [Genre.GAME]: '게임',
  [Genre.MILITARY]: '밀리터리',
  [Genre.SCIENCE_FICTION]: 'SF',
  [Genre.HORROR]: '공포',
  [Genre.ETC]: '기타',
};

export const AGE_RATING_LABELS: Record<AgeRating, string> = {
  [AgeRating.ALL]: '전체이용가',
  [AgeRating.AGE_12]: '12세 이용가',
  [AgeRating.AGE_15]: '15세 이용가',
  [AgeRating.AGE_19]: '19세 이용가',
};

export const STATUS_LABELS: Record<NovelStatus, string> = {
  [NovelStatus.ONGOING]: '연재중',
  [NovelStatus.COMPLETED]: '완결',
  [NovelStatus.HIATUS]: '휴재',
  [NovelStatus.DELETED]: '삭제',
};

export function getGenreLabel(genre: Genre | string): string {
  return GENRE_LABELS[genre as Genre] || genre;
}

export function getAgeRatingLabel(rating: AgeRating | number): string {
  return AGE_RATING_LABELS[rating as AgeRating] || String(rating);
}

export function getStatusLabel(status: NovelStatus | string): string {
  return STATUS_LABELS[status as NovelStatus] || status;
}
