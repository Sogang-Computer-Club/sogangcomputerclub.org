// Commitlint 설정
// Conventional Commits 형식 검증
//
// Note: Git hook 검증은 .pre-commit-config.yaml의 conventional-pre-commit이 담당합니다.
// 이 파일은 IDE 통합이나 수동 검증용으로 사용됩니다:
//   echo "feat: test" | npx commitlint

module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    // 허용되는 타입
    'type-enum': [
      2,
      'always',
      [
        'feat',
        'fix',
        'docs',
        'style',
        'refactor',
        'perf',
        'test',
        'build',
        'ci',
        'chore',
        'revert',
      ],
    ],
    // 한글 subject 허용 (case 검사 비활성화)
    'subject-case': [0],
    // subject 길이 제한
    'subject-max-length': [2, 'always', 100],
  },
};
