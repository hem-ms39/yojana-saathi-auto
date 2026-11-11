# Contributing

## Branching model (GitHub Flow)

- `main` is always deployable. **Nobody pushes to `main` directly.**
- Work on a short-lived branch named `<your-name>/<short-topic>`, e.g. `priya/qdrant-service`.
- Open a Pull Request into `main`. It can be merged only when:
  1. all CI checks are green, and
  2. at least **one teammate** has approved it.
- Use **"Squash and merge"** or **"Create a merge commit"** consistently (team decision: merge commit, so every author's commits stay visible in history).

## Commit messages — Conventional Commits

```
<type>(<scope>): <short summary>
```

| type | use for |
|---|---|
| `feat` | new feature |
| `fix` | bug fix |
| `test` | adding or fixing tests |
| `ci` / `cd` | pipeline changes |
| `build` | Dockerfiles, dependencies |
| `docs` | documentation |
| `chore` | maintenance |

Examples: `feat(agents): add eligibility scoring`, `ci: add frontend build job`.

## Before you push

Run the same checks CI runs for the part you touched (see README → *Run the checks locally*).

## Secrets

Never commit `.env` / `.env.local` or API keys. Copy `.env.example` and fill it locally.
The `secret-scan` CI job fails the build if a key is detected.

## One-time GitHub setup (repo owner)

1. **Settings → Collaborators**: add all 4 members with *Write* access.
2. **Settings → Branches → Add branch protection rule** for `main`:
   - Require a pull request before merging → Require approvals: **1**
   - Require status checks to pass → select `Backend · lint + tests`, `OCR service · tests`,
     `Frontend · lint + typecheck + build`, `Security · secret scan`, `Docker · build images + smoke test`
     (they appear in the list after the CI workflow has run once)
3. **Settings → Actions → General → Workflow permissions**: *Read and write permissions* (needed by CD to push images and create releases).
4. **Settings → Environments**: create `production` (optionally add required reviewers for a manual deployment gate).
5. Add deployment secrets/variables listed in the README.
