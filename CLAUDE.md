# FarmSure — Project Guide for Claude

## Test file generation rules

When writing or generating `tests/test_generated.py` (or any test file):

- **Never wrap code in markdown fences.** The file must be raw Python — no ` ```python ` at the top, no ` ``` ` at the bottom. The file is executed directly by pytest; markdown syntax causes a `SyntaxError`.
- **Always complete the file.** Every class and function must be fully closed before finishing. Never leave a `with`, `def`, `class`, or string literal open at the end of the file.
- **Use the existing conftest fixtures.** `conftest.py` already patches the database to `farmsure_test` and provides `make_user`, `make_claim`, and `seeded_admin` fixtures. Import and use them rather than re-implementing DB setup.
- **Do not redefine `clean_tables`.** It runs automatically (`autouse=True`) — all tables are wiped before every test.
- **Mock targets must match import paths.** If `get_connection` is called inside `farmsure.db.users`, patch it as `farmsure.db.users.get_connection`, not `farmsure.db.connection.get_connection`.
- **Avoid duplicate class names** with `tests/db/test_users.py`, `tests/db/test_claims.py`, and `tests/db/test_admins.py`. Suffix generated classes with `Mocked` (e.g. `TestUserLoginMocked`) when writing mock-based variants of existing tests.

## Project structure

```
farmsure/
├── db/
│   ├── connection.py   — get_connection(), _cur(), _row()
│   ├── users.py        — _hash(), init_db(), register_user(), login_user(), get_user(), update_user()
│   ├── claims.py       — create_claim(), get_user_claims(), get_claim_stats(), get_all_claims(), update_claim_status(), get_all_claim_stats()
│   └── admins.py       — init_admin_db(), login_admin()
└── ui/
    ├── theme.py         — C, STATUS_COLOR, STATUS_ACTIONS, CROP_TYPES, ISSUE_TYPES
    ├── widgets.py       — shared CTk widgets
    ├── portal/          — farmer portal (app, sidebar, pages/)
    └── backoffice/      — back-office app (app, pages/)

portal.py      — farmer portal entry point
backoffice.py  — back-office entry point
```

## Running tests

```bash
source venv/bin/activate
pytest                          # full suite (60 tests)
pytest tests/test_generated.py  # generated tests only
pytest --cov=farmsure --cov-report=term-missing  # with coverage
```

## Database

| Purpose     | Database        | URL env var          |
|-------------|-----------------|----------------------|
| Production  | `farmsure`      | `DATABASE_URL`       |
| Tests       | `farmsure_test` | `TEST_DATABASE_URL`  |

Both are on `localhost:5432` (local PostgreSQL). Docker runs a separate PostgreSQL instance but the app connects to the local one.

All credentials are in `.env` (gitignored). Never hardcode passwords or connection strings.
