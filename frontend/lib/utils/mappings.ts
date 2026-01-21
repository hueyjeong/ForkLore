import { Genre, AgeRating, NovelStatus } from '@/types/novels.types';

export const GENRE_LABELS: Record<Genre, string> = {
  [Genre.FANTASY]: '판타지',
  [Genre.ROMANCE]: '로맨스',
  [Genre.ACTION]: '액션',
  [Genre.THRILLER]: '스릴러',
  [Genre.MYSTERY]: '미스터리',
  [Genre.SF]: 'SF',
  [Genre.HISTORY]: '역사',
  [Genre.MODERN]: '현대',
  [Genre.MARTIAL]: '무협',
  [Genre.GAME]: '게임',
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
