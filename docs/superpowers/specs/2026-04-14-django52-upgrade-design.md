# Django 5.2 Upgrade — Design Spec

**Date:** 2026-04-14
**Target:** Django 5.2 (LTS)
**Current:** Django 4.2.22 (LTS)
**Strategy:** Two-phase — prepare on 4.2, then flip

---

## Scope

Five repositories, all upgraded together:

| Repo | Role | Django constraint |
|---|---|---|
| `janeway-upstream` | Core platform | `Django==4.2.22` (requirements.txt) |
| `wjs-profile-project` | JCOM profile plugin | `Django ~= 4.2` (setup.cfg) — **must be relaxed** |
| `wjs-submission-project` | Submission workflow | No hard upper bound |
| `wjs-utils-project` | Management commands | `Django >= 1.11` |
| `wjs-themes` | Frontend themes | No hard upper bound |

---

## Repo dependency order

```
janeway-upstream  ←  wjs-profile-project
                  ←  wjs-submission-project
                  ←  wjs-utils-project
                  ←  wjs-themes
```

Phase 1 prep branches can be opened and merged independently across all repos (they remain valid on 4.2). Phase 2 flips sequentially: `janeway-upstream` first, wjs repos after.

---

## Phase 1 — Prepare on Django 4.2

All changes in this phase must keep CI green on Django 4.2. Add a parallel `Django==5.2` tox environment to catch regressions early.

### 1A. Packages requiring forks

These packages have no PyPI-compatible release for Django 5.2. Fork under the Nephila/SISSA GitHub org, patch, and update `requirements.txt` to point at the fork.

#### `dynamicsites` (BirkbeckCTP/django-dynamicsites)

**Status:** NEEDS_FORK  
**Used by:** `janeway-upstream/requirements.txt` — but does **not** appear in `INSTALLED_APPS` or `MIDDLEWARE`. Confirm with production config whether this is active. If unused, remove the dependency entirely.  
**If still needed, required changes:**
- `render_to_response()` → removed in Django 5.0. Replace with `render(request, template, context)`, threading `request` through `process_request`.
- `django.utils.http.urlquote` → removed in Django 4.0. Replace with `urllib.parse.quote`.
- Old-style middleware (class-based, no `__call__`) → wrap with `django.utils.deprecation.MiddlewareMixin` or rewrite to new-style middleware with `__init__(self, get_response)` and `__call__`.

#### `django-bleach 3.1.0`

**Status:** NEEDS_FORK (latest PyPI version, classifiers stop at Django 4.2)  
**Used by:** `janeway-upstream` — `JanewayBleachField`, `JanewayBleachFormField` in `core/model_utils.py`  
**Required changes:**
1. Test against Django 5.2 first — the library uses no deprecated ORM internals and may work without code changes (classifiers are not code).
2. If `BleachField.formfield()` or widget rendering fails: update `MultiWidget.__init__` signature compatibility (Django 5.0 made `attrs` keyword-only).
3. Update classifiers to declare Django 5.x support and release from fork.

#### `django-mailgun 0.9.1`

**Status:** NEEDS_FORK (2015-era package, uses `six` for Py2/3 compat)  
**Used by:** `janeway-upstream/requirements.txt`  
**Required changes:**
- Remove all `six` imports: replace `six.text_type` → `str`, `six.string_types` → `str`, `six.moves` → direct stdlib.
- Update email backend class to match `django.core.mail.backends.base.BaseEmailBackend` current interface (verify `send_messages` signature).
- The package is ~150 lines; a full clean rewrite is feasible.

#### `foundationform` (BirkbeckCTP/django-foundation-form)

**Status:** LIKELY COMPATIBLE — verify before forking  
**Used by:** `janeway-upstream`  
**Assessment:** Source reviewed. Uses only `get_template()`, `template.render(context)` with dict context, and `Library` template tags. No deprecated Django internals found.  
**Action:** Run `manage.py check` and template render tests against Django 5.2. Fork and patch only if failures appear.

---

### 1B. PyPI version bumps

Replace pinned versions in `requirements.txt`. Corresponding constraint relaxations in wjs `setup.cfg` files where needed.

| Package | Current | Target | Migration notes |
|---|---|---|---|
| `django-modeltranslation` | 0.18.11 | 0.20.3 | 0.19.x enforces `required_languages` in `TranslationOptions`. Audit all `TranslationOptions` subclasses in `wjs-profile-project`. |
| `django-hijack` | 3.2.1 | 3.7.7 | 3.4.0 changed hijack button injection from middleware to template tag. Verify `HIJACK_USERS_ENABLED` guard; check templates that render hijack UI. |
| `mozilla-django-oidc` | 4.0.1 | 5.0.2 | `OIDC_RP_SIGN_ALGO` no longer has a default — must be set explicitly. Audit `utils/oidc.py` and any OIDC settings in deployment configs. |
| `django-bootstrap4` | 23.2 | 26.1 | Calendar-versioned. Audit templates using `{% bootstrap_form %}` and `{% bootstrap_button %}` — tag signatures changed between 23 and 26. |
| `django-fsm` | 2.8.2 | **replaced by `django-fsm-2==4.2.4`** | Drop-in replacement: same `django_fsm` import path. No `FSMTransitionMixin`/`fsm_admin` admin usage found — no code changes needed. Update `janeway-upstream/requirements.txt` **and** `wjs-profile-project/setup.cfg` (currently pins `django-fsm ~= 2.8.1` — change to `django-fsm-2>=4.2`). The two packages share the `django_fsm` namespace so cannot coexist; the swap must happen in both repos in the same release. |
| `swapper` | 1.3.0 | 1.4.0 | Declares Django 5.0 (not 5.2 explicitly). Minor risk — verify with test run. |
| `django-simple-history` | 3.10.1 | 3.11.0 | Declares Django 5.x. Low risk. |
| `django-autocomplete-light` | 3.12.1 | 3.12.1 (already latest) | Declares Django 5.1 but not 5.2. Run tests against 5.2; fork if autocomplete views break (likely a `QuerySet` API change). |

---

### 1C. Janeway internal code changes (`janeway-upstream`)

#### `create_forward_many_to_many_manager` — `core/model_utils.py:44,257`

Private Django internal imported from `django.db.models.fields.related_descriptors`. This API shifted in Django 5.x. Used by `M2MOrderedThroughDescriptor.related_manager_cls` to build a custom M2M manager with through-model ordering.

**Fix:** Replace the private factory call with a direct manager subclass. The only custom behaviour is `get_queryset` ordering:

```python
# Before (uses private API)
related_manager = create_forward_many_to_many_manager(
    related_model._default_manager.__class__,
    self.rel,
    reverse=self.reverse,
)
return create_m2m_ordered_through_manager(related_manager, self.rel)

# After (public API only)
# Remove create_forward_many_to_many_manager import
# Rewrite create_m2m_ordered_through_manager to subclass
# ManyToManyRelatedManager directly via the descriptor's existing cls
```

The custom manager must preserve: `get_queryset` with through-model ordering, `add()` with `allow_m2m_operation` context manager. The test coverage in `core/tests/test_model_utils.py` provides the safety net.

#### `queryset.extra(order_by=…)` — `core/model_utils.py:290`

Deprecated since Django 3.2. Used in `M2MOrderedThroughManager._apply_ordering`.

**Fix:** Replace `queryset.extra(order_by=[related_name])` with `queryset.order_by(related_name)`. Django accepts string-based cross-join ordering — the `related_name` value resolves to the through model's table alias correctly.

#### `USE_L10N = False` — `janeway_global_settings.py:270`

Silently ignored in Django 5.x (the setting was removed). Remove the line. If any templates relied on localisation being suppressed (date/number formatting), add explicit `{% localize off %}` blocks or configure `LOCALIZE_INPUT_FORMATS`.

#### `unique_together` deprecation (20+ model files)

Not a Django 5.2 blocker (removal scheduled for Django 6.0), but produces deprecation warnings that pollute CI output. Generate replacement migrations using `UniqueConstraint` for each affected model:

Affected files: `core/models.py`, `review/models.py`, `submission/models.py`, `repository/models.py`, `journal/models.py`, `metrics/models.py`, `production/models.py`, `proofing/models.py`, `cms/models.py`, `typesetting/models.py`.

Lower priority within Phase 1 — complete before Phase 2 but does not block other Phase 1 work.

#### `wjs-profile-project` Django constraint — `setup.cfg`

```
# Before
Django ~= 4.2

# After
Django >=4.2,<7
```

Apply the same `>=4.2,<7` bound to any other wjs package with a hard Django upper constraint.

---

## Phase 2 — Version flip

With all Phase 1 branches merged, apply in each repo:

**`janeway-upstream/requirements.txt`:**
```
Django==4.2.22  →  Django==5.2.x
```

**`janeway-upstream/pyproject.toml` tox deps:**
```
Django==4.2  →  Django==5.2
```

**wjs-profile-project `setup.cfg`:** already relaxed in Phase 1 — no change.

### Expected failure categories at flip time

| Area | Symptom | Fix |
|---|---|---|
| `CSRF_TRUSTED_ORIGINS` | `ImproperlyConfigured` at startup | Add `https://` scheme prefix to each origin in deployment configs |
| Password hashers | `ValueError` if `MD5PasswordHasher` / `SHA1PasswordHasher` listed explicitly | Remove those entries from `PASSWORD_HASHERS` |
| `FORM_RENDERER` | None expected — already set to `TemplatesSetting` | — |
| `unique_together` warnings | DeprecationWarning in test output | Resolved in Phase 1 |
| Forked packages | Template or import errors if fork patches are incomplete | Fix in fork, re-test |

### Phase 2 merge gate

- `python manage.py check --deploy` exits 0
- Full test suite passes on `Django==5.2`
- Dev server starts and renders admin, submission workflow, and journal homepage without errors

---

## Testing strategy

- **Phase 1 PRs:** CI matrix runs `Django==4.2` and `Django==5.2` in parallel (tox). Changes must be green on both.
- **Forked packages:** Each fork gets a standalone test: install against Django 5.2, import, run package test suite.
- **Phase 2 PRs:** CI runs `Django==5.2` only.
- **Integration smoke test:** After Phase 2 merge, start dev server and verify: admin login, journal article submission form, site routing (domain→journal resolution), OIDC login flow.
