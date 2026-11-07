"""Native admission boundary; preparation is limited to marked tiny controls."""
NATIVE_CAPABILITY = object()


def require_fields(rules, fixture, capability=None):
    if capability is not NATIVE_CAPABILITY and not (
        rules.get('software_control') is True and rules['fields'] and
        fixture['p'] <= 211 and all(v['p'] <= 211 for v in rules['fields'])):
        raise ValueError('A14 native admission required')
    if fixture['p'] not in {v['p'] for v in rules['fields']}:
        raise ValueError('field differs from declared rules')
