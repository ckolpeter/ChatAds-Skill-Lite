#!/usr/bin/env python3
"""Offline chatads.brief validation and explicit legacy intake conversion (stdlib only)."""
import argparse
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / 'schemas/chatads.brief.v1.schema.json'


class ValidationError(ValueError):
    pass


def _check(value, schema, path='$'):
    """Evaluate the deliberately small keyword subset used by our bundled schema."""
    if 'const' in schema and value != schema['const']:
        raise ValidationError(f'{path}: unsupported contract')
    types = schema.get('type', [])
    if isinstance(types, str):
        types = [types]
    valid = {'null': value is None, 'string': isinstance(value, str),
             'object': isinstance(value, dict), 'array': isinstance(value, list),
             'number': type(value) in (int, float) and math.isfinite(value),
             'integer': type(value) is int}
    if types and not any(valid[t] for t in types):
        raise ValidationError(f'{path}: incorrect type')
    if value is None:
        return
    if isinstance(value, dict):
        props = schema['properties']
        if set(value) - set(props) or set(schema['required']) - set(value):
            raise ValidationError(f'{path}: missing or forbidden fields')
        for key, item in value.items():
            _check(item, props[key], f'{path}.{key}')
    elif isinstance(value, list):
        for i, item in enumerate(value):
            _check(item, schema['items'], f'{path}[{i}]')
    elif isinstance(value, str):
        if not value.strip() or len(value) < schema.get('minLength', 0):
            raise ValidationError(f'{path}: empty text')
        if 'pattern' in schema and not re.search(schema['pattern'], value):
            raise ValidationError(f'{path}: invalid format')
        # Defense in depth, not a general secret/identity detector. Never echo values.
        if re.search(r'(?i)(bearer\s+\S+|sk-[a-z0-9]{20,}|act_\d+|\b\d{10,}\b|(?:api[_ -]?key|access[_ -]?token|password|cookie|account[_ -]?id)\s*[:=])', value):
            raise ValidationError(f'{path}: sensitive-looking content')
    elif type(value) in (int, float) and value < schema.get('minimum', -math.inf):
        raise ValidationError(f'{path}: below minimum')


def validate(data):
    _check(data, json.loads(SCHEMA.read_text(encoding='utf-8')))
    return data


def from_beginner(data):
    if not isinstance(data, dict):
        raise ValidationError('beginner: expected object')
    allowed = {'schema_version', 'mode', 'offer', 'customer', 'goal', 'market',
               'landing_url', 'spend_limit', 'measurement', 'external_writes'}
    if set(data) - allowed or data.get('schema_version') != '1.1' or data.get('mode') != 'beginner':
        raise ValidationError('beginner: unsupported version, mode or fields')
    if data.get('external_writes') is not False:
        raise ValidationError('beginner: external_writes must be false')
    brief = json.loads((ROOT / 'templates/business-brief.json').read_text())
    for key in ('offer', 'customer', 'goal', 'market', 'landing_url', 'spend_limit', 'measurement'):
        if key in data:
            brief[key] = data[key]
    brief['open_questions'] = [f'Confirm {k}.' for k in ('business', 'offer', 'customer', 'goal', 'market', 'landing_url', 'measurement') if brief[k] is None]
    brief['open_questions'] += [f'Confirm spend_limit.{k}.' for k, v in brief['spend_limit'].items() if v is None] if isinstance(brief['spend_limit'], dict) else []
    brief['open_questions'].append('Supply evidence for any proposed claims.')
    return validate(brief)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['validate', 'from-beginner'])
    parser.add_argument('input')
    args = parser.parse_args(argv)
    try:
        def pairs(items):
            result = {}
            for key, value in items:
                if key in result:
                    raise ValidationError('duplicate JSON key')
                result[key] = value
            return result
        data = json.loads(Path(args.input).read_text(encoding='utf-8'), object_pairs_hook=pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(ValidationError('non-finite JSON number')))
        result = validate(data) if args.command == 'validate' else from_beginner(data)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except (ValueError, OSError):
        print('BRIEF_BLOCKED: invalid input; inspect locally without logging sensitive values', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
