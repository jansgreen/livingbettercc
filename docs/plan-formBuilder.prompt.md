Plan: Harden FormBuilder shared links on Heroku (no 500s)

Goals
- Prevent 500 errors when accessing shared FormBuilder links.
- Ensure robust redirects even if URL names/namespaces differ across environments.
- Preserve existing authorization rules (owner, staff, tecnico).

Steps
1. Define reverse_safe helper
- Implement a wrapper around Django reverse() that returns a fallback path on NoReverseMatch.
- Optional: log NoReverseMatch details for diagnostics.

2. Replace risky reverse calls
- In render_form(): wrap 'facilitador_register' with reverse_safe; default to settings.LOGIN_URL or '/accounts/login/'.
- In share_with_facilitadores(): wrap 'formbuilder:shared_completed_form' with fallback to 'shared_completed_form' or '/formbuilder/shared/<pk>/'.
- In shared_completed_form(): wrap 'formbuilder:completed_forms_detail' with fallback to 'completed_forms_detail' or '/formbuilder/completed/<pk>/'.

3. Add fallbacks for register routes
- For tecnico flows: use reverse_safe('tecnico_register', default=settings.LOGIN_URL or '/accounts/login/').
- Always append next=<return_path> to preserve user flow after registration.

4. Verify URL namespaces in urls.py
- Confirm 'formbuilder' namespace is defined and consistent across local/Heroku.
- Ensure named routes exist: 'shared_completed_form', 'completed_forms_detail', 'facilitador_register', 'tecnico_register'.

5. Add tests for shared link flows
- Cases: unauthenticated share link → redirects to tecnico_register with next; authenticated owner/staff/tecnico → redirects to detail; authenticated non-authorized → 404.
- Include tests for reverse fallbacks by temporarily removing namespace in test URLconf.

6. Deploy and tail Heroku logs
- Push changes; verify no 500 on shared link access.
- Check logs for NoReverseMatch occurrences; confirm fallbacks used.

7. Document changes and rollout plan
- Update README/docs with safe reverse strategy and URL naming expectations.
- Add a brief troubleshooting section.

Acceptance Criteria
- Shared link pages never produce HTTP 500; they redirect or 404 per rules.
- No NoReverseMatch exceptions in Heroku logs for these views.
- Unit tests pass for all access paths.

Quick commands
- Run locally:
  - python manage.py check
  - python manage.py test authentication.formbuilder
- Deploy + verify:
  - git push heroku master
  - heroku logs -n 200
