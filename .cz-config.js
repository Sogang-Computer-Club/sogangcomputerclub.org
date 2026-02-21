// Commitizen 설정 (한글 프롬프트)
// 사용법: cd frontend && npm run cz

module.exports = {
  types: [
    { value: 'feat', name: 'feat:     새로운 기능' },
    { value: 'fix', name: 'fix:      버그 수정' },
    { value: 'docs', name: 'docs:     문서 변경' },
    { value: 'style', name: 'style:    코드 포맷팅 (기능 변경 없음)' },
    { value: 'refactor', name: 'refactor: 코드 리팩토링' },
    { value: 'perf', name: 'perf:     성능 개선' },
    { value: 'test', name: 'test:     테스트 추가/수정' },
    { value: 'build', name: 'build:    빌드 시스템 변경' },
    { value: 'ci', name: 'ci:       CI 설정 변경' },
    { value: 'chore', name: 'chore:    기타 유지보수' },
    { value: 'revert', name: 'revert:   커밋 되돌리기' },
  ],

  scopes: [
    { name: 'frontend' },
    { name: 'backend' },
    { name: 'infra' },
    { name: 'docs' },
    { name: 'ci' },
  ],

  messages: {
    type: '변경 유형 선택:',
    scope: '변경 범위 (선택사항, Enter로 건너뛰기):',
    subject: '짧은 설명 (필수):\n',
    body: '자세한 설명 (선택사항, Enter로 건너뛰기):\n',
    breaking: '주요 변경사항 (BREAKING CHANGE) 설명 (선택사항):\n',
    footer: '관련 이슈 번호 (예: #123, 선택사항):\n',
    confirmCommit: '위 내용으로 커밋하시겠습니까?',
  },

  allowCustomScopes: true,
  allowBreakingChanges: ['feat', 'fix'],
  skipQuestions: ['body', 'breaking', 'footer'],
  subjectLimit: 100,
};
