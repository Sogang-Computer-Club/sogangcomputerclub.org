# Contributing to Sogang Computer Club Website

Thank you for contributing to the Sogang Computer Club website project! This document outlines the workflow for contributing to this fork-based project.

## Repository Structure

- **Upstream**: `Sogang-Computer-Club/sogangcomputerclub.org` (original repository)
- **Fork**: `revenantonthemission/sogangcomputerclub.org` (your development repository)

## Workflow: GitHub Flow

We use **GitHub Flow**, a simple, branch-based workflow:

1. `master` is always deployable
2. Create feature branches from `master`
3. Open Pull Requests for review
4. Merge to `master` after approval

## Getting Started

### 1. Keep Your Fork Synced

Your fork automatically syncs with upstream daily via the `sync-upstream.yml` workflow. You can also manually trigger it:

```bash
# Via GitHub UI: Actions → Sync Fork with Upstream → Run workflow

# Or using gh CLI:
gh workflow run sync-upstream.yml
```

### 2. Create a Feature Branch

Always create a new branch for your changes:

```bash
# Sync with latest master first
git checkout master
git pull origin master

# Create a feature branch
git checkout -b feature/your-feature-name
```

**Branch Naming Conventions:**
- `feature/` - New features
- `bugfix/` or `fix/` - Bug fixes
- `hotfix/` - Urgent fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions or changes
- `chore/` - Maintenance tasks

### 3. Develop and Test

Make your changes and test locally:

```bash
# Backend (Python/FastAPI)
cd /path/to/project
uv sync
uv run pytest tests/

# Frontend (SvelteKit)
cd frontend
npm install
npm run test
npm run build
```

### 4. Commit Your Changes

Write clear, concise commit messages:

```bash
git add .
git commit -m "feat: add user authentication feature"
```

**Commit Message Format:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Test changes
- `chore:` - Maintenance

### 5. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 6. Open a Pull Request

#### To Your Fork (for testing):
1. Go to your fork on GitHub
2. Click "Pull requests" → "New pull request"
3. Base: `master` ← Compare: `feature/your-feature-name`
4. Add description and submit

The `validate-pr.yml` workflow will run automatically to check:
- Branch naming conventions
- Merge conflicts
- CI tests (via `backend-ci.yml` and `frontend-ci.yml`)

#### To Upstream (for contribution):
1. Go to the upstream repository: `Sogang-Computer-Club/sogangcomputerclub.org`
2. Click "Pull requests" → "New pull request" → "compare across forks"
3. Base: `Sogang-Computer-Club:master` ← Compare: `revenantonthemission:feature/your-feature-name`
4. Add detailed description explaining your changes
5. Wait for upstream maintainers to review

## CI/CD Workflows

### Automated Workflows on Your Fork

- **`backend-ci.yml`**: Runs Python tests on backend changes
- **`frontend-ci.yml`**: Runs TypeScript/Svelte tests on frontend changes
- **`docker-build.yml`**: Builds Docker images for feature branches
- **`integration-tests.yml`**: Runs integration tests
- **`security-scan.yml`**: Scans for vulnerabilities
- **`sync-upstream.yml`**: Syncs your fork with upstream
- **`validate-pr.yml`**: Validates PRs before merge

### Workflows Trigger Patterns

Most workflows trigger on:
- Push to `master` or feature branches (`feature/*`, `bugfix/*`, etc.)
- Pull requests to `master`

## Code Review Process

1. **Self-review**: Check your own code before opening a PR
2. **Automated checks**: Ensure all CI workflows pass
3. **Peer review**: Address feedback from reviewers
4. **Approval**: Get approval before merging
5. **Merge**: Squash and merge or merge commit (depending on project preference)

## Deployment

### Staging
- Triggered on push to `staging` branch (if configured)
- Deploys to staging environment for testing

### Production
- Triggered on push to upstream's `master` branch
- Only upstream maintainers can deploy to production

## Troubleshooting

### Sync Conflicts

If automatic sync fails:

```bash
# Manual sync
git checkout master
git fetch upstream
git merge upstream/master
# Resolve conflicts if any
git push origin master
```

### Failed CI Checks

1. Check the workflow logs on GitHub Actions
2. Run tests locally to reproduce the issue
3. Fix the issue and push again

### Merge Conflicts in PR

```bash
# Update your feature branch with latest master
git checkout feature/your-feature-name
git fetch origin
git merge origin/master
# Resolve conflicts
git push origin feature/your-feature-name
```

## Questions?

If you have any questions, please open an issue or reach out to the maintainers.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
