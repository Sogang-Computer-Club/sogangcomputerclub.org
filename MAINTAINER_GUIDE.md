# Maintainer Guide

This guide is for project maintainers who review and merge contributions.

## Table of Contents

- [Responsibilities](#responsibilities)
- [PR Review Process](#pr-review-process)
- [Merge Guidelines](#merge-guidelines)
- [Release Process](#release-process)
- [Automated Workflows](#automated-workflows)
- [Managing Contributors](#managing-contributors)

---

## Responsibilities

As a maintainer, you are responsible for:

- Reviewing and merging pull requests
- Ensuring code quality and project standards
- Responding to issues and questions
- Managing releases
- Maintaining CI/CD pipelines
- Welcoming new contributors

---

## PR Review Process

### 1. Initial Triage

When a PR is opened:

1. **Automated checks run automatically:**
   - PR validation (title, description, branch name)
   - CI tests (backend, frontend, integration)
   - Security scans
   - Auto-labeling

2. **Check for:**
   - Clear PR description
   - Linked issues
   - Appropriate labels
   - Passing CI checks

### 2. Code Review

**What to look for:**

- **Correctness**: Does the code do what it claims?
- **Quality**: Is the code well-written and maintainable?
- **Tests**: Are there adequate tests?
- **Documentation**: Is documentation updated?
- **Security**: Are there any security concerns?
- **Performance**: Any performance regressions?
- **Breaking changes**: Are they necessary and documented?

**Review checklist:**

```markdown
- [ ] Code follows project style guidelines
- [ ] Tests are comprehensive and passing
- [ ] Documentation is updated
- [ ] No security vulnerabilities introduced
- [ ] No performance regressions
- [ ] Breaking changes are justified and documented
- [ ] Commit messages are clear
```

### 3. Providing Feedback

**Good feedback is:**

- **Specific**: Point to exact lines or files
- **Constructive**: Suggest improvements, don't just criticize
- **Kind**: Remember there's a person on the other end
- **Educational**: Explain the "why" behind suggestions

**Example feedback:**

```markdown
Good:
"Consider using a Set here instead of an Array for O(1) lookups. 
This will improve performance when checking for duplicates."

Bad:
"This is slow."
```

### 4. Request Changes or Approve

- **Request Changes**: For issues that must be fixed before merge
- **Comment**: For suggestions that don't block merge
- **Approve**: When the PR meets all criteria

---

## Merge Guidelines

### When to Merge

Merge a PR when:

1. All CI checks pass
2. At least one maintainer approval
3. No outstanding change requests
4. No merge conflicts
5. Contributor has signed off (if required)

### Merge Methods

**Squash and Merge** (Default, Recommended)
- Use for: Most PRs
- Keeps history clean
- Single commit per feature

**Merge Commit**
- Use for: Large features with meaningful commit history
- Preserves all commits

**Rebase and Merge**
- Use for: Clean, linear history required
- Only for PRs from repository (not forks)

### Auto-Merge

For PRs from the same repository (not forks):

1. Add `auto-merge` label
2. Approve the PR
3. Wait for all checks to pass
4. PR will be automatically merged

---

## Release Process

### Creating a Release

#### Method 1: Via Git Tag

```bash
# Create and push a tag
git tag -a v1.2.3 -m "Release version 1.2.3"
git push origin v1.2.3
```

#### Method 2: Via GitHub Actions

1. Go to Actions → "Create Release"
2. Click "Run workflow"
3. Enter version (e.g., `v1.2.3`)
4. Click "Run workflow"

### Release Versioning

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (v1.0.0 → v2.0.0): Breaking changes
- **MINOR** (v1.1.0 → v1.2.0): New features, backward compatible
- **PATCH** (v1.1.1 → v1.1.2): Bug fixes, backward compatible

### Pre-releases

For alpha/beta/rc releases:

```bash
git tag -a v1.2.3-alpha.1 -m "Alpha release"
git push origin v1.2.3-alpha.1
```

---

## Automated Workflows

### PR Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `pr-validation.yml` | PR opened/edited | Validates PR format and content |
| `pr-labeler.yml` | PR opened/updated | Auto-labels based on files/size/type |
| `pr-auto-assign.yml` | PR opened | Assigns reviewers, welcomes contributors |
| `backend-ci.yml` | Push/PR | Runs backend tests |
| `frontend-ci.yml` | Push/PR | Runs frontend tests |
| `integration-tests.yml` | Push/PR | Runs integration tests |
| `security-scan.yml` | Push/PR | Security scanning |

### Maintenance Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `stale.yml` | Daily | Marks and closes stale PRs/issues |
| `auto-merge.yml` | Review/Checks | Auto-merges approved PRs |
| `release.yml` | Tag push | Creates releases with changelog |

### Deployment Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `deploy-production.yml` | Push to master | Deploys to production |

---

## Managing Contributors

### Welcoming New Contributors

When someone makes their first contribution:

1. Thank them for their contribution
2. Be extra patient and helpful
3. Guide them through the process
4. Encourage future contributions

**Template response:**

```markdown
Welcome! Thank you for your first contribution to this project!

I'll review this PR shortly. In the meantime, make sure all CI checks are passing.

If you have any questions, feel free to ask!
```

### Handling Difficult Situations

**Spam PRs:**
- Close immediately
- Add "spam" label
- Report if necessary

**Low-quality PRs:**
- Politely explain what needs improvement
- Link to contribution guidelines
- Offer to help if genuine effort

**Abandoned PRs:**
- Comment asking for status
- If no response after 7 days, add "stale" label
- Auto-close after 30 days total inactivity
- Consider taking over if valuable

**Conflicts between contributors:**
- Stay neutral and professional  
- Focus on technical merits
- Refer to code of conduct if needed
- Make final decision if necessary

---

## Labels

### Standard Labels

**Type:**
- `type: feature` - New features
- `type: bug` - Bug fixes
- `type: documentation` - Documentation changes
- `type: refactor` - Code refactoring
- `type: test` - Test improvements
- `type: ci/cd` - CI/CD changes

**Status:**
- `status: draft` - Work in progress
- `status: ready` - Ready for review
- `needs review` - Awaiting review
- `stale` - Inactive PR/issue

**Size:**
- `size/xs` - Tiny changes (1-10 lines)
- `size/s` - Small changes (11-50 lines)
- `size/m` - Medium changes (51-200 lines)
- `size/l` - Large changes (201-500 lines)
- `size/xl` - Extra large changes (500+ lines)

**Priority:**
- `priority: high` - Urgent
- `priority: medium` - Normal
- `priority: low` - Nice to have

**Other:**
- `external contribution` - From fork
- `auto-merge` - Enable auto-merge
- `security` - Security-related
- `breaking change` - Contains breaking changes

---

## Best Practices

### Communication

- Respond to PRs within 2-3 business days
- Set clear expectations
- Be transparent about timeline
- Mention if you need more time

### Code Quality

- Enforce consistent standards
- Don't be too strict on minor issues
- Focus on what matters (correctness, security, performance)
- Allow contributor's personal style within reason

### Decision Making

- Make decisions based on project goals
- Explain reasoning
- Be open to discussion
- Final decision with kindness

---

## Useful Commands

### Review a PR locally

```bash
# Fetch PR
gh pr checkout 123

# Run tests
uv run pytest tests/
cd frontend && npm run test

# View changes
git diff master...HEAD

# Return to master
git checkout master
```

### Merge a PR

```bash
# Via gh CLI
gh pr merge 123 --squash --delete-branch

# Via git
git checkout master
git merge --squash pr-branch
git commit
git push origin master
```

### Create a release

```bash
# Create tag
git tag -a v1.2.3 -m "Release 1.2.3"
git push origin v1.2.3

# Or use gh
gh release create v1.2.3 --generate-notes
```

---

## Getting Help

If you're unsure about something:

1. Check existing PRs for similar situations
2. Discuss with other maintainers
3. Ask in project discussions
4. Refer to GitHub documentation

Remember: It's okay to ask for help!
