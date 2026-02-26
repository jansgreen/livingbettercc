# Security Hardening Checklist

Date: 2026-02-26
Environment: Heroku `prod` (`livingbettercc`)

## Completed

- Created production backup:
  - Backup ID: `b005`
  - Command used: `heroku pg:backups:capture --remote prod`
- Created release tag in git:
  - Tag: `release-2026-02-26-hardening`
  - Points to commit: `c9de3459`
- Rotated Django `SECRET_KEY` in Heroku config vars.
- Removed legacy Stripe fallback vars from Heroku:
  - `STRIPE_SECRET_KEY`
  - `STRIPE_PUBLISHABLE_KEY`
  - `STRIPE_WEBHOOK_SECRET`
- Verified app health:
  - Dyno status up
  - `GET /` returned HTTP `200`

## Pending (Manual Rotation Required)

These values were exposed and must be rotated at provider level:

- Stripe:
  - `STRIPE_LIVE_SECRET_KEY`
  - `STRIPE_LIVE_PUBLISHABLE_KEY` (optional to rotate, safe to rotate anyway)
  - `STRIPE_LIVE_WEBHOOK_SECRET`
  - `STRIPE_TEST_SECRET_KEY`
  - `STRIPE_TEST_PUBLISHABLE_KEY`
  - `STRIPE_TEST_WEBHOOK_SECRET`
- Cloudinary:
  - `CLOUDINARY_API_SECRET`
  - `CLOUDINARY_URL`
- Email app password:
  - `EMAIL_HOST_PASSWORD`
- Postgres credentials (`DATABASE_URL`) if exposed publicly:
  - Rotate Heroku Postgres credentials and update app if required.

## Stripe Notes

- Ensure TEST webhook secret and LIVE webhook secret are different.
- Create/verify two webhook endpoints (test/live) pointing to:
  - `https://www.livingbettercc.com/payments/stripe/webhook/`

## Heroku Commands for Updating Secrets

```bash
# Example: set new Stripe live values
heroku config:set STRIPE_LIVE_SECRET_KEY=sk_live_new --remote prod
heroku config:set STRIPE_LIVE_PUBLISHABLE_KEY=pk_live_new --remote prod
heroku config:set STRIPE_LIVE_WEBHOOK_SECRET=whsec_live_new --remote prod

# Example: set new Stripe test values
heroku config:set STRIPE_TEST_SECRET_KEY=sk_test_new --remote prod
heroku config:set STRIPE_TEST_PUBLISHABLE_KEY=pk_test_new --remote prod
heroku config:set STRIPE_TEST_WEBHOOK_SECRET=whsec_test_new --remote prod
```

## Verification Commands

```bash
# Check Heroku app status
heroku ps --remote prod

# Check recent logs
heroku logs --tail --remote prod

# Check Stripe vars only
heroku config --remote prod | grep STRIPE
```

