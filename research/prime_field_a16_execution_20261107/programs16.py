"""Disjoint target-horizon program contracts, no first8-from24 cold shortcut."""
from copy import deepcopy

PROGRAMS=(
    dict(id='norm8',base='norm',horizon=8,base_size=None,source=True),
    dict(id='hybrid8',base='hybrid',horizon=8,base_size=16,source=True),
    dict(id='known32_8',base='known32',horizon=8,base_size=32,source=False),
    dict(id='known48_8',base='known48',horizon=8,base_size=48,source=False),
    dict(id='known48_24',base='known48',horizon=24,base_size=48,source=False))


def get(identifier):
    try:return deepcopy(next(v for v in PROGRAMS if v['id']==identifier))
    except StopIteration:raise ValueError('unknown target-effort program') from None


def rules_for(rules,identifier):
    program=get(identifier);out=deepcopy(rules)
    out.update(program_id=identifier,base_kind=program['base'],target_queries_per_point=program['horizon'],
        target_prefixes=[24] if program['horizon']==24 else list(rules['short_target_prefixes']))
    out['maximum_target_cache_points']=rules['targets']*(1+len(rules['target_policies'])*(program['horizon']-1))
    if not rules.get('software_control') and out['maximum_target_cache_points'] not in (176,560):
        raise ValueError('native target cache bound differs from prospective program')
    return out


def descriptors(rules):
    index=0
    for field in rules['fields']:
        for ci in range(rules['curves_per_field']):
            cid='p'+str(field['p'])+'-i'+str(ci)
            for p in PROGRAMS:
                current=rules_for(rules,p['id'])
                schedules=[kind+str(seed) for seed in rules['seeds'] for kind in ('ap','hash')] if p['source'] else ['known']
                for schedule in schedules:
                    for policy in rules['target_policies']:
                        for budget in current['target_prefixes']:
                            for scope in (rules['norm_scopes'] if p['source'] else [rules['known_scope']]):
                                yield index,dict(cell_id=cid,program=p['id'],base_arm=p['base'],target_horizon=p['horizon'],
                                    source_schedule=schedule,source_prefix=rules['sources'] if p['source'] else 0,
                                    target_policy=policy,target_prefix=budget,scope=scope)
                                index+=1


def validate_descriptor(rules,descriptor):
    p=get(descriptor['program']);current=rules_for(rules,p['id'])
    if descriptor['base_arm']!=p['base'] or descriptor['target_horizon']!=p['horizon'] or descriptor['target_prefix'] not in current['target_prefixes']:
        raise ValueError('program/horizon/prefix descriptor mismatch')
    if (not p['source'] and (descriptor['source_schedule']!='known' or descriptor['source_prefix']!=0 or descriptor['scope']!='supplied')):
        raise ValueError('source-free program gained source work or wrong scope')
    return current


def recipe_prefix(short,long,targets,policies):
    for policy in policies:
        if len(short['policies'][policy])!=targets or len(long['policies'][policy])!=targets:
            raise ValueError('symbolic recipe target census')
        for a,b in zip(short['policies'][policy],long['policies'][policy],strict=True):
            if len(a)!=8 or len(b)!=24 or b[:8]!=a:
                raise ValueError('independent8/24 symbolic recipe prefix mismatch')
    return True
