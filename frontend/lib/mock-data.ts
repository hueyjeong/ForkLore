import { Novel, RankingNovel, CommunityPost } from './types';

export * from './types';

// =============================================================================
// Ranking Novels (Extended with status and tags)
// =============================================================================

export const RANKING_NOVELS: RankingNovel[] = [
  { 
    id: 1, 
    title: 'The Shadow of the Highborn', 
    author: 'Elena Vance', 
    views: '1.2M', 
    rating: 4.8, 
    coverUrl: 'https://images.unsplash.com/photo-1629196914168-3a26476d90e6?q=80&w=2787&auto=format&fit=crop', 
    status: '연재중', 
    tags: ['판타지', '로맨스'],
    description: 'A story about the shadow of the highborn.',
    episodeCount: 120,
    recommendCount: 4500,
    isExclusive: true,
    isPremium: false,
    updatedAt: '2026-01-17'
  },
  { 
    id: 2, 
    title: 'Return of the SSS-Class Hunter', 
    author: 'Jin Woo', 
    views: '980K', 
    rating: 4.7, 
    coverUrl: 'https://images.unsplash.com/photo-1541963463532-d68292c34b19?q=80&w=2788&auto=format&fit=crop', 
    status: '연재중', 
    tags: ['액션', '헌터물'],
    description: 'The return of the SSS-class hunter.',
    episodeCount: 85,
    recommendCount: 3200,
    isExclusive: false,
    isPremium: true,
    updatedAt: '2026-01-16'
  },
  { 
    id: 3, 
    title: 'I Became the Villainess', 
    author: 'Aria Rose', 
    views: '850K', 
    rating: 4.9, 
    coverUrl: 'https://images.unsplash.com/photo-1518544974780-3df139b81a4d?q=80&w=2787&auto=format&fit=crop', 
    status: '완결', 
    tags: ['로맨스', '빙의물'],
    description: 'How I became the villainess.',
    episodeCount: 150,
    recommendCount: 5600,
    isExclusive: true,
    isPremium: true,
    updatedAt: '2026-01-15'
  },
  { 
    id: 4, 
    title: 'Level Up Alone', 
    author: 'System User', 
    views: '720K', 
    rating: 4.6, 
    coverUrl: 'https://images.unsplash.com/photo-1535905557558-afc4877a26fc?q=80&w=2787&auto=format&fit=crop', 
    status: '연재중', 
    tags: ['액션', '시스템물'],
    description: 'Leveling up alone in a system world.',
    episodeCount: 60,
    recommendCount: 2100,
    isExclusive: false,
    isPremium: false,
    updatedAt: '2026-01-14'
  },
  { 
    id: 5, 
    title: 'The Alchemy of Stars', 
    author: 'Luna Sol', 
    views: '650K', 
    rating: 4.8, 
    coverUrl: 'https://images.unsplash.com/photo-1532012197267-da84d127e765?q=80&w=2787&auto=format&fit=crop', 
    status: '완결', 
    tags: ['판타지', '마법'],
    description: 'Discovering the alchemy of stars.',
    episodeCount: 200,
    recommendCount: 7800,
    isExclusive: true,
    isPremium: false,
    updatedAt: '2026-01-13'
  },
];

// =============================================================================
// Banner Slides
// =============================================================================

export const BANNER_SLIDES = [
  { id: 1, image: 'https://images.unsplash.com/photo-1629196914168-3a26476d90e6?q=80&w=2787&auto=format&fit=crop', link: '/novels/1' },
  { id: 2, image: 'https://images.unsplash.com/photo-1541963463532-d68292c34b19?q=80&w=2788&auto=format&fit=crop', link: '/novels/2' },
  { id: 3, image: 'https://images.unsplash.com/photo-1518544974780-3df139b81a4d?q=80&w=2787&auto=format&fit=crop', link: '/novels/3' },
  { id: 4, image: 'https://images.unsplash.com/photo-1535905557558-afc4877a26fc?q=80&w=2787&auto=format&fit=crop', link: '/novels/4' },
  { id: 5, image: 'https://images.unsplash.com/photo-1532012197267-da84d127e765?q=80&w=2787&auto=format&fit=crop', link: '/novels/5' },
];

// =============================================================================
// Novels List (20 items for Novels page)
// =============================================================================

const COVER_IMAGES = [
  'https://images.unsplash.com/photo-1629196914168-3a26476d90e6?q=80&w=2787&auto=format&fit=crop',
  'https://images.unsplash.com/photo-1541963463532-d68292c34b19?q=80&w=2788&auto=format&fit=crop',
  'https://images.unsplash.com/photo-1518544974780-3df139b81a4d?q=80&w=2787&auto=format&fit=crop',
  'https://images.unsplash.com/photo-1535905557558-afc4877a26fc?q=80&w=2787&auto=format&fit=crop',
  'https://images.unsplash.com/photo-1532012197267-da84d127e765?q=80&w=2787&auto=format&fit=crop',
];

export const NOVELS_LIST: Novel[] = [
  { id: '1', title: '그림자 속의 귀족', author: '엘레나 밴스', coverUrl: COVER_IMAGES[0], genre: '판타지', rating: 4.8, views: '1.2M', status: '연재중', tags: ['판타지', '로맨스'], updatedAt: '2026-01-17', description: '그림자 속의 귀족 이야기', episodeCount: 120, recommendCount: 4500, isExclusive: true, isPremium: false },
  { id: '2', title: 'SSS급 헌터의 귀환', author: '진우', coverUrl: COVER_IMAGES[1], genre: '액션', rating: 4.7, views: '980K', status: '연재중', tags: ['헌터물', '액션'], updatedAt: '2026-01-16', description: 'SSS급 헌터의 귀환 이야기', episodeCount: 85, recommendCount: 3200, isExclusive: false, isPremium: true },
  { id: '3', title: '악녀가 되어버렸다', author: '아리아 로즈', coverUrl: COVER_IMAGES[2], genre: '로맨스', rating: 4.9, views: '850K', status: '완결', tags: ['빙의물', '로맨스'], updatedAt: '2026-01-15', description: '악녀가 되어버렸다 이야기', episodeCount: 150, recommendCount: 5600, isExclusive: true, isPremium: true },
  { id: '4', title: '나 혼자만 레벨업', author: '시스템 유저', coverUrl: COVER_IMAGES[3], genre: '액션', rating: 4.6, views: '720K', status: '연재중', tags: ['시스템물', '성장물'], updatedAt: '2026-01-14', description: '나 혼자만 레벨업 이야기', episodeCount: 60, recommendCount: 2100, isExclusive: false, isPremium: false },
  { id: '5', title: '별들의 연금술', author: '루나 솔', coverUrl: COVER_IMAGES[4], genre: '판타지', rating: 4.8, views: '650K', status: '완결', tags: ['마법', '판타지'], updatedAt: '2026-01-13', description: '별들의 연금술 이야기', episodeCount: 200, recommendCount: 7800, isExclusive: true, isPremium: false },
  { id: '6', title: '전생 검사의 무림 생존기', author: '검왕', coverUrl: COVER_IMAGES[0], genre: '무협', rating: 4.5, views: '520K', status: '연재중', tags: ['무협', '전생'], updatedAt: '2026-01-12', description: '전생 검사의 무림 생존기 이야기', episodeCount: 110, recommendCount: 3900, isExclusive: false, isPremium: false },
  { id: '7', title: '마왕님, 출근하셨습니다', author: '직장인 A', coverUrl: COVER_IMAGES[1], genre: '일상', rating: 4.4, views: '480K', status: '연재중', tags: ['일상', '코미디'], updatedAt: '2026-01-11', description: '마왕님, 출근하셨습니다 이야기', episodeCount: 95, recommendCount: 2800, isExclusive: false, isPremium: false },
  { id: '8', title: '시간을 되돌리는 능력자', author: '회귀자', coverUrl: COVER_IMAGES[2], genre: 'SF', rating: 4.7, views: '450K', status: '연재중', tags: ['회귀물', 'SF'], updatedAt: '2026-01-10', description: '시간을 되돌리는 능력자 이야기', episodeCount: 130, recommendCount: 4200, isExclusive: true, isPremium: false },
  { id: '9', title: '귀신 보는 형사', author: '미스터리안', coverUrl: COVER_IMAGES[3], genre: '미스터리', rating: 4.6, views: '420K', status: '완결', tags: ['미스터리', '공포'], updatedAt: '2026-01-09', description: '귀신 보는 형사 이야기', episodeCount: 80, recommendCount: 2500, isExclusive: false, isPremium: true },
  { id: '10', title: '흑막 보스의 딸로 살아남기', author: '생존자 B', coverUrl: COVER_IMAGES[4], genre: '로맨스', rating: 4.8, views: '400K', status: '연재중', tags: ['빙의물', '생존'], updatedAt: '2026-01-08', description: '흑막 보스의 딸로 살아남기 이야기', episodeCount: 140, recommendCount: 4800, isExclusive: true, isPremium: true },
  { id: '11', title: '던전 청소부의 일상', author: '청소왕', coverUrl: COVER_IMAGES[0], genre: '판타지', rating: 4.3, views: '380K', status: '연재중', tags: ['던전물', '일상'], updatedAt: '2026-01-07', description: '던전 청소부의 일상 이야기', episodeCount: 70, recommendCount: 1800, isExclusive: false, isPremium: false },
  { id: '12', title: '황제폐하의 사랑받는 신부', author: '로맨티스트', coverUrl: COVER_IMAGES[1], genre: '로맨스', rating: 4.9, views: '360K', status: '완결', tags: ['궁정물', '로맨스'], updatedAt: '2026-01-06', description: '황제폐하의 사랑받는 신부 이야기', episodeCount: 160, recommendCount: 6200, isExclusive: true, isPremium: true },
  { id: '13', title: '버그 플레이어', author: '게이머 C', coverUrl: COVER_IMAGES[2], genre: 'SF', rating: 4.5, views: '340K', status: '연재중', tags: ['게임물', '시스템물'], updatedAt: '2026-01-05', description: '버그 플레이어 이야기', episodeCount: 90, recommendCount: 3100, isExclusive: false, isPremium: false },
  { id: '14', title: '무림 최강 의원', author: '의선', coverUrl: COVER_IMAGES[3], genre: '무협', rating: 4.6, views: '320K', status: '연재중', tags: ['무협', '의학'], updatedAt: '2026-01-04', description: '무림 최강 의원 이야기', episodeCount: 125, recommendCount: 4400, isExclusive: false, isPremium: false },
  { id: '15', title: '망나니 공작의 반전', author: '반전왕', coverUrl: COVER_IMAGES[4], genre: '판타지', rating: 4.7, views: '300K', status: '완결', tags: ['성장물', '복수극'], updatedAt: '2026-01-03', description: '망나니 공작의 반전 이야기', episodeCount: 105, recommendCount: 3700, isExclusive: true, isPremium: false },
  { id: '16', title: '마법 학교 열등생', author: '마법사 D', coverUrl: COVER_IMAGES[0], genre: '판타지', rating: 4.4, views: '280K', status: '연재중', tags: ['학원물', '마법'], updatedAt: '2026-01-02', description: '마법 학교 열등생 이야기', episodeCount: 88, recommendCount: 2900, isExclusive: false, isPremium: false },
  { id: '17', title: '좀비 세상에서 살아남기', author: '생존왕', coverUrl: COVER_IMAGES[1], genre: '공포', rating: 4.5, views: '260K', status: '연재중', tags: ['좀비물', '생존'], updatedAt: '2026-01-01', description: '좀비 세상에서 살아남기 이야기', episodeCount: 115, recommendCount: 3500, isExclusive: false, isPremium: false },
  { id: '18', title: '대기업 회장님의 비서입니다', author: '비서 E', coverUrl: COVER_IMAGES[2], genre: '로맨스', rating: 4.6, views: '240K', status: '완결', tags: ['현대물', '로맨스'], updatedAt: '2025-12-31', description: '대기업 회장님의 비서입니다 이야기', episodeCount: 145, recommendCount: 4900, isExclusive: true, isPremium: true },
  { id: '19', title: '이세계 요리왕', author: '셰프 F', coverUrl: COVER_IMAGES[3], genre: '일상', rating: 4.7, views: '220K', status: '연재중', tags: ['이세계', '요리'], updatedAt: '2025-12-30', description: '이세계 요리왕 이야기', episodeCount: 100, recommendCount: 3300, isExclusive: false, isPremium: false },
  { id: '20', title: '천재 탐정의 사건 파일', author: '탐정 G', coverUrl: COVER_IMAGES[4], genre: '미스터리', rating: 4.8, views: '200K', status: '연재중', tags: ['미스터리', '추리'], updatedAt: '2025-12-29', description: '천재 탐정의 사건 파일 이야기', episodeCount: 135, recommendCount: 4600, isExclusive: false, isPremium: false },
];

// =============================================================================
// Community Posts (15 items for Community page)
// =============================================================================

export const COMMUNITY_POSTS: CommunityPost[] = [
  { id: '1', title: '[필독] 커뮤니티 이용 가이드', author: '운영자', category: '공지', commentCount: 156, likeCount: 892, createdAt: '2026-01-10', isPinned: true },
  { id: '2', title: '[공지] 신규 작품 추천 이벤트 안내', author: '운영자', category: '공지', commentCount: 89, likeCount: 567, createdAt: '2026-01-15', isPinned: true },
  { id: '3', title: '그림자 속의 귀족 45화 해석 토론', author: '팬아트러버', category: '작품토론', commentCount: 234, likeCount: 456, createdAt: '2026-01-17', isPinned: false },
  { id: '4', title: 'SSS급 헌터 최신화 반전 대박...', author: '헌터덕후', category: '작품토론', commentCount: 189, likeCount: 345, createdAt: '2026-01-16', isPinned: false },
  { id: '5', title: '요즘 읽을만한 로맨스 추천해주세요', author: '로맨스독자', category: '자유', commentCount: 67, likeCount: 123, createdAt: '2026-01-16', isPinned: false },
  { id: '6', title: '무협물 입문자인데 추천 부탁드려요', author: '무협초보', category: '자유', commentCount: 45, likeCount: 89, createdAt: '2026-01-15', isPinned: false },
  { id: '7', title: '악녀 작품 결말 어떻게 생각하세요?', author: '결말토론러', category: '작품토론', commentCount: 312, likeCount: 678, createdAt: '2026-01-14', isPinned: false },
  { id: '8', title: '웹소설 읽다가 밤샜네요 ㅋㅋ', author: '밤샘독서', category: '자유', commentCount: 23, likeCount: 156, createdAt: '2026-01-14', isPinned: false },
  { id: '9', title: '레벨업 시스템물 최고 명작은?', author: '시스템물팬', category: '작품토론', commentCount: 178, likeCount: 234, createdAt: '2026-01-13', isPinned: false },
  { id: '10', title: '신규 가입 인사드립니다!', author: '뉴비독자', category: '자유', commentCount: 12, likeCount: 45, createdAt: '2026-01-13', isPinned: false },
  { id: '11', title: '별들의 연금술 세계관 정리', author: '세계관덕후', category: '작품토론', commentCount: 89, likeCount: 567, createdAt: '2026-01-12', isPinned: false },
  { id: '12', title: '작가님들 응원 댓글 남기기 캠페인', author: '응원단장', category: '자유', commentCount: 234, likeCount: 789, createdAt: '2026-01-11', isPinned: false },
  { id: '13', title: '[공지] 서버 점검 안내 (1/20)', author: '운영자', category: '공지', commentCount: 34, likeCount: 123, createdAt: '2026-01-10', isPinned: false },
  { id: '14', title: '던전물 vs 헌터물 차이가 뭔가요?', author: '장르궁금이', category: '자유', commentCount: 56, likeCount: 178, createdAt: '2026-01-09', isPinned: false },
  { id: '15', title: '회귀물 클리셰 정리해봄', author: '클리셰박사', category: '작품토론', commentCount: 145, likeCount: 432, createdAt: '2026-01-08', isPinned: false },
];
