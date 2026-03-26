## Documentation Audit Report - 2026-03-26

### Overall Score: 4.2/10

| Category | Score | Worker | Issues |
|----------|-------|--------|--------|
| Documentation Structure | 3.4/10 | ln-611 | 18 issues (H:5 M:8 L:5) |
| Semantic Content | 8.1/10 | ln-612 | 26 issues across 14 docs (H:4 M:12 L:10) |
| Code Comments | 4.8/10 | ln-613 | 12 issues (H:2 M:4 L:6) |
| Fact Accuracy | 0.0/10 | ln-614 | 14 issues (C:1 H:7 M:5 L:1) |

### Critical Findings

- [ ] **[Fact Accuracy]** `.env.example:16-27` - Kafka configuration block still present after Kafka removal (commit 59b3a8b). Misleads new developers during setup. **Action:** Remove Kafka config section entirely.
- [ ] **[Fact Accuracy]** `CLAUDE.md:8` - States "SvelteKit 5" but package.json has `@sveltejs/kit: ^2.16.0` (SvelteKit 2.x). **Action:** Change to "SvelteKit 2" or "SvelteKit 2 + Svelte 5".
- [ ] **[Fact Accuracy]** `README.md:10` - States "SvelteKit 5, Svelte 5" — SvelteKit is 2.x. Public-facing README. **Action:** Change to "SvelteKit 2, Svelte 5".
- [ ] **[Fact Accuracy]** `MAINTAINER_GUIDE.md:199-219` - References 5 workflow files that don't exist (`pr-auto-assign.yml`, `codeql.yml`, `stale.yml`, `auto-merge.yml`, `deploy-production.yml`). **Action:** Update to match actual `.github/workflows/` contents.
- [ ] **[Fact Accuracy]** `docs/getting-started.md:76` - Documents `docker-compose --profile kafka up -d` but Kafka profile was removed. **Action:** Remove Kafka profile references.
- [ ] **[Fact Accuracy]** `docs/testing.md:12-13,257` - References `tests/test_integration.py`, `locustfile.py`, `docker-compose.test.yml` — none exist. **Action:** Remove or create.
- [ ] **[Fact Accuracy]** `docs/frontend.md:353`, `docs/testing.md:169`, `docs/getting-started.md:188` - Documents `npm run test:coverage` and `npm run lint` — not defined in package.json. **Action:** Add scripts or remove references.
- [ ] **[Structure]** `CLAUDE.md:24-36` - Does not link to individual docs/ files (architecture, backend, frontend, etc.) — only links to `/docs/` directory. **Action:** Add explicit links.
- [ ] **[Structure]** `.agent/rules/contribution-guide.md` - ~90% duplication of CONTRIBUTING.md with minor divergences. **Action:** Delete and reference CONTRIBUTING.md directly.
- [ ] **[Structure]** `docs/backend.md` (347 lines), `docs/frontend.md` (383 lines) - Exceed 300-line guide limit with ~200 lines of code blocks each. **Action:** Remove code examples, link to source files.
- [ ] **[Comments]** `frontend/src/routes/notice/recruitment/+page.svelte:48-51` - Commented-out code block. **Action:** Remove; git history preserves it.
- [ ] **[Comments]** `scripts/migrate_db.py:13-16,69-74,99` - Stale stream-of-consciousness comments from initial development. **Action:** Remove thinking-out-loud comments.

### Advisory Findings

(Context-validated: AWS infrastructure is kept as backup but not actively built — downgraded per project decision)

- **[Fact Accuracy]** `docs/infrastructure.md:12,17` - EC2 shown as t3.small, terraform.tfvars has t3.micro. *[AWS backup — not actively deployed]*
- **[Fact Accuracy]** `infrastructure/README.md:135-142` - Cost table overstated (t3.small vs actual t3.micro). *[AWS backup]*
- **[Fact Accuracy]** `infrastructure/README.md:190` - Claims 7-day backup but rds.tf has 1 day. *[AWS backup]*
- **[Fact Accuracy]** `docker-compose.aws.yml:17` - Sets `EVENT_BACKEND=sqs` but app no longer reads this variable. *[AWS backup]*
- **[Semantic]** `docs/architecture.md:145-171` - Event architecture section describes Kafka/SQS in detail despite being disabled. *[Planned: event system simplified to NullEventPublisher]*
- **[Semantic]** `docs/architecture.md:136-138` - Frontend diagram references AuthStore which was removed. *[Planned: auth removed in 8c8dd54]*
- **[Semantic]** `docs/project/codebase_audit.md` - Findings H5, H7, H9 already addressed by recent commits. *[Stale — recent fixes applied]*

### Recommended Actions

| Priority | Action | Location | Category |
|----------|--------|----------|----------|
| High | Remove Kafka config from .env.example | `.env.example:16-27` | Fact Accuracy |
| High | Fix SvelteKit version in CLAUDE.md and README.md | `CLAUDE.md:8`, `README.md:10` | Fact Accuracy |
| High | Remove nonexistent workflow references | `MAINTAINER_GUIDE.md:199-219` | Fact Accuracy |
| High | Remove Kafka profile references from getting-started | `docs/getting-started.md:76,82` | Fact Accuracy |
| High | Delete duplicate contribution-guide.md | `.agent/rules/contribution-guide.md` | Structure |
| High | Remove nonexistent file references from testing.md | `docs/testing.md:12-13,257` | Fact Accuracy |
| Medium | Remove or add missing npm scripts (test:coverage, lint) | `frontend/package.json` + 3 docs | Fact Accuracy |
| Medium | Update event system description in architecture.md | `docs/architecture.md:145-171` | Semantic |
| Medium | Remove auth patterns from frontend.md | `docs/frontend.md:196` | Semantic |
| Medium | Remove dead code/stale comments | 4 files across frontend + scripts | Comments |
| Medium | Add links to individual docs from CLAUDE.md | `CLAUDE.md:24-36` | Structure |
| Medium | Compress oversized docs (backend.md, frontend.md, testing.md) | `docs/` | Structure |
| Low | Remove WHAT-style and section divider comments | `app/main.py` | Comments |
| Low | Add JSDoc to undocumented utility functions | `frontend/src/lib/utils/` | Comments |
| Low | Remove stale plan docs or archive | `docs/plans/` | Structure |
