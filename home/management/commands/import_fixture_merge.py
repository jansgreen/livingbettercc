from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from django.apps import apps
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction


@dataclass
class ImportStats:
    created: int = 0
    updated: int = 0
    skipped_existing: int = 0
    deferred_fk: int = 0
    deferred_m2m: int = 0
    failed: int = 0


def _is_fk_violation(exc: IntegrityError) -> bool:
    cause = getattr(exc, "__cause__", None)
    name = getattr(cause, "__class__", type("X", (), {})).__name__
    sqlstate = getattr(cause, "sqlstate", None)
    if name == "ForeignKeyViolation":
        return True
    if sqlstate == "23503":  # PostgreSQL foreign_key_violation
        return True
    return False


def _is_unique_violation(exc: IntegrityError) -> bool:
    cause = getattr(exc, "__cause__", None)
    name = getattr(cause, "__class__", type("X", (), {})).__name__
    sqlstate = getattr(cause, "sqlstate", None)
    if name == "UniqueViolation":
        return True
    if sqlstate == "23505":  # PostgreSQL unique_violation
        return True
    return False


class _DeferRecord(Exception):
    def __init__(self, kind: str, detail: str = ""):
        super().__init__(detail)
        self.kind = kind
        self.detail = detail


def _normalize_unique_field_lookup(model, field_name: str, scalar_kwargs: dict[str, Any]) -> tuple[str, Any] | None:
    """Return a lookup key/value suitable for QuerySet.filter() for a field name.

    For FK fields, uses the underlying *_id attribute when possible.
    """
    field = model._meta.get_field(field_name)
    if getattr(field, "many_to_many", False):
        return None

    if getattr(field, "is_relation", False) and (
        getattr(field, "many_to_one", False) or getattr(field, "one_to_one", False)
    ):
        lookup_key = field.attname
        if lookup_key not in scalar_kwargs:
            return None
        return lookup_key, scalar_kwargs[lookup_key]

    if field_name not in scalar_kwargs:
        return None
    return field_name, scalar_kwargs[field_name]


def _candidate_unique_lookups(
    model,
    scalar_kwargs: dict[str, Any],
) -> list[dict[str, Any]]:
    lookups: list[dict[str, Any]] = []

    # Multi-field uniqueness first (unique_together + UniqueConstraint(fields=[...]))
    for ut in getattr(model._meta, "unique_together", []) or []:
        parts: list[tuple[str, Any]] = []
        for name in ut:
            normalized = _normalize_unique_field_lookup(model, name, scalar_kwargs)
            if normalized is None:
                parts = []
                break
            parts.append(normalized)
        if parts:
            lookups.append(dict(parts))

    for constraint in getattr(model._meta, "constraints", []) or []:
        constraint_fields = getattr(constraint, "fields", None)
        if not constraint_fields:
            continue
        parts: list[tuple[str, Any]] = []
        for name in constraint_fields:
            normalized = _normalize_unique_field_lookup(model, name, scalar_kwargs)
            if normalized is None:
                parts = []
                break
            parts.append(normalized)
        if parts:
            lookups.append(dict(parts))

    # Single unique fields
    for field in model._meta.get_fields():
        if not getattr(field, "unique", False):
            continue
        name = getattr(field, "name", None)
        if not name:
            continue
        normalized = _normalize_unique_field_lookup(model, name, scalar_kwargs)
        if normalized is None:
            continue
        key, value = normalized
        if value is None:
            continue
        lookups.append({key: value})

    # De-dup preserving order
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for lookup in lookups:
        # Some unique fields may be JSON/list-like; build a stable string key.
        try:
            key = json.dumps(lookup, sort_keys=True, ensure_ascii=False, default=str)
        except Exception:
            key = str(sorted(lookup.items(), key=lambda kv: kv[0]))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(lookup)

    return deduped


class Command(BaseCommand):
    help = (
        "Merge-import a JSON fixture into the current database without wiping it. "
        "Creates missing rows, updates existing ones when a unique match is found, "
        "and defers rows that fail due to FK ordering (multiple passes)."
    )

    def add_arguments(self, parser):
        parser.add_argument("fixture", help="Path to a JSON fixture (list of objects)")
        parser.add_argument(
            "--database",
            default="default",
            help="Database alias to use (default: 'default')",
        )
        parser.add_argument(
            "--skip-existing",
            action="store_true",
            help="If a row already exists (by pk/unique), don't update it.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Do not write anything; just report what would happen.",
        )
        parser.add_argument(
            "--max-passes",
            type=int,
            default=5,
            help="Max passes to resolve FK ordering (default: 5)",
        )

        parser.add_argument(
            "--pending-out",
            default="",
            help="If set, write remaining pending records to this JSON file.",
        )

        parser.add_argument(
            "--print-pending-models",
            action="store_true",
            help="Print a per-model breakdown of remaining pending objects.",
        )

        parser.add_argument(
            "--log-deferred",
            type=int,
            default=0,
            help="If >0, print up to N deferred records with the reason (default: 0).",
        )

        parser.add_argument(
            "--skip-missing-m2m-targets",
            action="store_true",
            help="Skip missing M2M targets (e.g. old permissions/contenttypes) instead of deferring forever.",
        )

    def handle(self, *args, **options):
        fixture_path: str = options["fixture"]
        using: str = options["database"]
        skip_existing: bool = options["skip_existing"]
        dry_run: bool = options["dry_run"]
        max_passes: int = options["max_passes"]
        pending_out: str = options["pending_out"]
        print_pending_models: bool = options["print_pending_models"]
        log_deferred_limit: int = options["log_deferred"]
        skip_missing_m2m_targets: bool = options["skip_missing_m2m_targets"]

        with open(fixture_path, "r", encoding="utf-8") as f:
            records = json.load(f)

        if not isinstance(records, list):
            raise SystemExit("Fixture must be a JSON list")

        pending = records
        stats = ImportStats()
        hard_failures: list[tuple[str, Any, str]] = []
        defer_reasons: dict[str, dict[str, int]] = {}
        pk_map: dict[tuple[str, int], int] = {}
        logged_deferred = 0

        for pass_num in range(1, max_passes + 1):
            if not pending:
                break

            self.stdout.write(
                self.style.NOTICE(
                    f"Pass {pass_num}/{max_passes}: attempting {len(pending)} objects..."
                )
            )

            next_pending: list[dict[str, Any]] = []

            for rec in pending:
                model_label = rec.get("model")
                pk = rec.get("pk")
                fields = rec.get("fields") or {}

                if not model_label or not isinstance(fields, dict):
                    stats.failed += 1
                    hard_failures.append((str(model_label), pk, "invalid record"))
                    continue

                Model = apps.get_model(model_label)
                if Model is None:
                    stats.failed += 1
                    hard_failures.append((model_label, pk, "unknown model"))
                    continue

                m2m_values: dict[str, Any] = {}
                scalar_kwargs: dict[str, Any] = {}
                should_defer = False

                try:
                    for name, value in fields.items():
                        field = Model._meta.get_field(name)

                        if field.many_to_many:
                            m2m_values[name] = value
                            continue

                        if field.is_relation and (field.many_to_one or field.one_to_one):
                            # ForeignKey / OneToOne
                            if isinstance(value, (list, tuple)):
                                rel_model = field.remote_field.model
                                # natural key
                                try:
                                    rel_obj = rel_model._default_manager.db_manager(using).get_by_natural_key(*value)
                                    scalar_kwargs[field.attname] = rel_obj.pk
                                except Exception as e:
                                    stats.deferred_fk += 1
                                    should_defer = True
                                    defer_reasons.setdefault(model_label, {}).setdefault("natural_fk_missing", 0)
                                    defer_reasons[model_label]["natural_fk_missing"] += 1
                                    if log_deferred_limit and logged_deferred < log_deferred_limit:
                                        self.stdout.write(
                                            self.style.WARNING(
                                                f"DEFER {model_label} pk={pk} FK {name}={value}: {e}"
                                            )
                                        )
                                        logged_deferred += 1
                                    break
                            else:
                                # If the related object's PK was remapped, apply it.
                                if isinstance(value, int):
                                    rel_label = field.remote_field.model._meta.label_lower
                                    scalar_kwargs[field.attname] = pk_map.get((rel_label, value), value)
                                else:
                                    scalar_kwargs[field.attname] = value
                            continue

                        scalar_kwargs[name] = value

                    if should_defer:
                        next_pending.append(rec)
                        continue

                    # Validate FK/OneToOne numeric references early to avoid opaque FK violations.
                    for rel_field in Model._meta.fields:
                        if not rel_field.is_relation or not (rel_field.many_to_one or rel_field.one_to_one):
                            continue
                        attname = rel_field.attname
                        if attname not in scalar_kwargs:
                            continue
                        rel_pk = scalar_kwargs.get(attname)
                        if rel_pk is None:
                            continue
                        rel_model = rel_field.remote_field.model
                        if not rel_model._default_manager.using(using).filter(pk=rel_pk).exists():
                            stats.deferred_fk += 1
                            next_pending.append(rec)
                            defer_reasons.setdefault(model_label, {}).setdefault("fk_missing", 0)
                            defer_reasons[model_label]["fk_missing"] += 1
                            if log_deferred_limit and logged_deferred < log_deferred_limit:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"DEFER {model_label} pk={pk} FK missing {attname}={rel_pk}"
                                    )
                                )
                                logged_deferred += 1
                            should_defer = True
                            break

                    if should_defer:
                        continue

                    # Resolve M2M targets before writing anything so we can defer cleanly.
                    m2m_ids: dict[str, list[int]] = {}
                    for m2m_name, m2m_val in m2m_values.items():
                        try:
                            rel_manager = None
                            # We don't have an instance yet; resolve via model field.
                            m2m_field = Model._meta.get_field(m2m_name)
                            rel_model = m2m_field.remote_field.model
                            m2m_ids[m2m_name] = self._resolve_m2m_ids_model(
                                rel_model,
                                m2m_val,
                                using,
                                pk_map,
                                skip_missing=skip_missing_m2m_targets,
                            )
                        except Exception as e:
                            stats.deferred_m2m += 1
                            next_pending.append(rec)
                            defer_reasons.setdefault(model_label, {}).setdefault("m2m", 0)
                            defer_reasons[model_label]["m2m"] += 1
                            if log_deferred_limit and logged_deferred < log_deferred_limit:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"DEFER {model_label} pk={pk} M2M {m2m_name}: {e}"
                                    )
                                )
                                logged_deferred += 1
                            should_defer = True
                            break

                    if should_defer:
                        continue

                    existing = None
                    if pk is not None:
                        existing = Model._default_manager.using(using).filter(pk=pk).first()

                    if existing is None:
                        for lookup in _candidate_unique_lookups(Model, scalar_kwargs):
                            existing = Model._default_manager.using(using).filter(**lookup).first()
                            if existing is not None:
                                break

                    if existing is not None:
                        # Record PK remap if this fixture PK maps to an existing different PK.
                        if pk is not None and existing.pk != pk:
                            pk_map[(model_label, int(pk))] = int(existing.pk)

                        if skip_existing:
                            stats.skipped_existing += 1
                            continue

                        for key, val in scalar_kwargs.items():
                            setattr(existing, key, val)

                        if not dry_run:
                            with transaction.atomic(using=using):
                                existing.save(using=using)

                                for m2m_name, ids in m2m_ids.items():
                                    rel_manager = getattr(existing, m2m_name)
                                    rel_manager.set(ids)

                        stats.updated += 1
                        continue

                    obj = Model(**scalar_kwargs)
                    if pk is not None:
                        obj.pk = pk

                    if not dry_run:
                        with transaction.atomic(using=using):
                            obj.save(using=using)

                            for m2m_name, ids in m2m_ids.items():
                                rel_manager = getattr(obj, m2m_name)
                                rel_manager.set(ids)

                    stats.created += 1

                except IntegrityError as e:
                    if _is_fk_violation(e):
                        stats.deferred_fk += 1
                        next_pending.append(rec)
                        defer_reasons.setdefault(model_label, {}).setdefault("fk", 0)
                        defer_reasons[model_label]["fk"] += 1
                        continue

                    if _is_unique_violation(e):
                        # Retry as update using unique constraints.
                        existing = None
                        for lookup in _candidate_unique_lookups(Model, scalar_kwargs):
                            existing = Model._default_manager.using(using).filter(**lookup).first()
                            if existing is not None:
                                break

                        if existing is None:
                            stats.failed += 1
                            hard_failures.append((model_label, pk, f"unique violation but no match: {e}"))
                            continue

                        # Record PK remap if fixture PK collides with an existing row.
                        if pk is not None and existing.pk != pk:
                            pk_map[(model_label, int(pk))] = int(existing.pk)

                        if skip_existing:
                            stats.skipped_existing += 1
                            continue

                        for key, val in scalar_kwargs.items():
                            setattr(existing, key, val)

                        if not dry_run:
                            with transaction.atomic(using=using):
                                existing.save(using=using)

                                try:
                                    for m2m_name, m2m_val in m2m_values.items():
                                        rel_manager = getattr(existing, m2m_name)
                                        rel_manager.set(
                                            self._resolve_m2m_ids(rel_manager, m2m_val, using, pk_map)
                                        )
                                except Exception:
                                    stats.deferred_m2m += 1
                                    next_pending.append(rec)
                                    continue

                        stats.updated += 1
                        continue

                    stats.failed += 1
                    hard_failures.append((model_label, pk, str(e)))

                except Exception as e:
                    # Catch-all: treat as deferred once (often missing natural keys or ordering).
                    next_pending.append(rec)
                    defer_reasons.setdefault(model_label, {}).setdefault("other", 0)
                    defer_reasons[model_label]["other"] += 1
                    if log_deferred_limit and logged_deferred < log_deferred_limit:
                        self.stdout.write(
                            self.style.WARNING(f"DEFER {model_label} pk={pk} OTHER: {e}")
                        )
                        logged_deferred += 1

            # De-duplicate pending records for the next pass to avoid growth.
            deduped: list[dict[str, Any]] = []
            seen: set[tuple[str, Any, str]] = set()
            for rec in next_pending:
                model_label = rec.get("model") or "<unknown>"
                pk = rec.get("pk")
                fields = rec.get("fields") or {}
                fields_key = ""
                if pk is None:
                    try:
                        fields_key = json.dumps(fields, sort_keys=True, ensure_ascii=False)
                    except Exception:
                        fields_key = str(fields)
                key = (model_label, pk, fields_key)
                if key in seen:
                    continue
                seen.add(key)
                deduped.append(rec)

            pending = deduped

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. created={stats.created} updated={stats.updated} "
                f"skipped_existing={stats.skipped_existing} "
                f"deferred_fk={stats.deferred_fk} deferred_m2m={stats.deferred_m2m} "
                f"failed={stats.failed} remaining={len(pending)}"
            )
        )

        if pending:
            self.stdout.write(self.style.WARNING(f"Still pending after passes: {len(pending)}"))

        if print_pending_models and pending:
            per_model: dict[str, int] = {}
            for rec in pending:
                per_model[rec.get("model") or "<unknown>"] = per_model.get(rec.get("model") or "<unknown>", 0) + 1
            for model_label, count in sorted(per_model.items(), key=lambda kv: (-kv[1], kv[0])):
                self.stdout.write(f"- pending {model_label}: {count}")

        if pending_out and pending:
            with open(pending_out, "w", encoding="utf-8") as f:
                json.dump(pending, f, ensure_ascii=False, indent=2)
            self.stdout.write(self.style.WARNING(f"Wrote pending records to: {pending_out}"))

        if defer_reasons:
            self.stdout.write("Defer reasons (counts):")
            for model_label, reasons in sorted(defer_reasons.items(), key=lambda kv: kv[0]):
                reasons_str = ", ".join(f"{k}={v}" for k, v in sorted(reasons.items()))
                self.stdout.write(f"- {model_label}: {reasons_str}")

        if hard_failures:
            self.stdout.write(self.style.ERROR("Some objects failed permanently:"))
            for model_label, pk, msg in hard_failures[:25]:
                self.stdout.write(f"- {model_label} pk={pk}: {msg}")
            if len(hard_failures) > 25:
                self.stdout.write(f"... and {len(hard_failures) - 25} more")

    def _resolve_m2m_ids(
        self,
        rel_manager,
        raw_value: Any,
        using: str,
        pk_map: dict[tuple[str, int], int],
    ) -> list[int]:
        # Fixture format: list of PKs or list of natural keys.
        if raw_value is None:
            return []
        if not isinstance(raw_value, list):
            return []

        rel_model = rel_manager.model
        rel_label = rel_model._meta.label_lower
        resolved: list[int] = []
        for item in raw_value:
            if isinstance(item, int):
                resolved.append(pk_map.get((rel_label, item), item))
                continue
            if isinstance(item, (list, tuple)):
                obj = rel_model._default_manager.using(using).get_by_natural_key(*item)
                resolved.append(obj.pk)
                continue
        return resolved

    def _resolve_m2m_ids_model(
        self,
        rel_model,
        raw_value: Any,
        using: str,
        pk_map: dict[tuple[str, int], int],
        skip_missing: bool,
    ) -> list[int]:
        if raw_value is None:
            return []
        if not isinstance(raw_value, list):
            return []

        rel_label = rel_model._meta.label_lower
        resolved: list[int] = []
        for item in raw_value:
            if isinstance(item, int):
                resolved.append(pk_map.get((rel_label, item), item))
                continue
            if isinstance(item, (list, tuple)):
                try:
                    obj = rel_model._default_manager.db_manager(using).get_by_natural_key(*item)
                    resolved.append(obj.pk)
                except ObjectDoesNotExist:
                    if skip_missing:
                        continue
                    raise
                continue
        return resolved
