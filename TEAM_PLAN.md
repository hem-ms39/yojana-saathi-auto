# Team Plan

Yojana Saathi was first built as a single-developer prototype. For the DevOps course the
codebase is migrated into this team repository, with each module owned by one member and
delivered through pull requests, an automated CI pipeline, and continuous deployment.

## Module ownership

| | Member 1 | Member 2 | Member 3 | Member 4 |
|---|---|---|---|---|
| **Area** | Backend core & AI agents | Services, data & integrations | Frontend | OCR service & DevOps lead |
| **Code** | `backend/agents`, `backend/models`, `backend/config.py`, `backend/main.py`, routers: chat, explain, compare, schemes, health | `backend/services`, routers: auth, apply, forms, voice, scheme_chat, `scripts/`, `data/` | `frontend/`, `prototype/` | `m3_workspace/`, `docs/`, `.github/`, `docker-compose.yml` |
| **Tests** | `backend/tests` (health, schemas, eligibility, profile extractor) | `backend/tests/test_schemes_api.py` | lint + typecheck + build | `m3_workspace/tests` |
| **CI job** | `backend` | `secret-scan`, `docker-smoke` | `frontend` | `ocr-service` |
| **CD / Docker** | `backend/Dockerfile` | image smoke test | `frontend/Dockerfile` | `m3_workspace/Dockerfile`, compose, `cd.yml` |

## Delivery phases

| Phase | Goal | Done when |
|---|---|---|
| 1. Setup | Repo, configs, data models, scaffolds | Each module has a skeleton on `main` |
| 2. Core | Services, agents, OCR engine, UI components | Core logic merged |
| 3. Features | API routers, pages, OCR API | App runs end-to-end locally |
| 4. Quality | Unit tests, lint fixes, dependency security bump | All checks pass locally |
| 5. CI | GitHub Actions CI, one job per member | PRs blocked unless green |
| 6. CD | Dockerfiles, compose, image publishing, deployment | Merge to `main` ships automatically |

Each phase is merged completely before the next one starts.
