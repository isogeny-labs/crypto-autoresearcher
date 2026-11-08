"""Deterministic exclusions from hash-bound, already exposed public inputs."""
from pathlib import Path
import argparse
import hashlib
import json


def inventory(prior, public):
    if type(prior) is not list:
        raise ValueError('prior exclusion list required')
    exclusions=set()
    for pair in prior:
        if (type(pair) is not list or len(pair)!=2 or any(type(v) is not int for v in pair)
                or pair[0]<=3 or not 0<=pair[1]<pair[0]):
            raise ValueError('canonical prior (p,j) pair')
        if tuple(pair) in exclusions:raise ValueError('duplicate prior pair')
        exclusions.add(tuple(pair))
    exposed=set()
    for row in public['curves']:
        c=row['model'];p=c['p'];a=c['a'];b=c['b']
        if any(type(v) is not int for v in [p,a,b]) or p<=3 or not 0<=a<p or not 0<=b<p:
            raise ValueError('canonical exposed model')
        denominator=(4*a**3+27*b*b)%p
        if not denominator:raise ValueError('singular exposed model')
        exposed.add((p,1728*4*a**3*pow(denominator,-1,p)%p))
    return {'schema':'controlled-followup-v6.exclusions/v1',
            'prior_pairs':len(exclusions),'exposed_domains':len(public['curves']),
            'distinct_exposed_pairs':len(exposed),
            'excluded_p_j':[list(pair) for pair in sorted(exclusions|exposed)],
            'new_entropy_draws':0}


def checked(path, expected):
    p=Path(path)
    if not p.is_file() or p.is_symlink() or p.stat().st_size>256<<20:
        raise ValueError('bounded regular input required')
    b=p.read_bytes()
    if hashlib.sha256(b).hexdigest()!=expected:raise ValueError('input digest differs')
    return json.loads(b)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prior-config',required=True);p.add_argument('--prior-sha256',required=True)
    p.add_argument('--exposed-input',required=True);p.add_argument('--input-sha256',required=True)
    p.add_argument('--out',required=True);a=p.parse_args()
    prior=checked(a.prior_config,a.prior_sha256)
    exposed=checked(a.exposed_input,a.input_sha256)
    result=inventory(prior['sampler']['excluded_p_j'],exposed['public'])
    result['provenance']={'prior_config_sha256':a.prior_sha256,'exposed_input_sha256':a.input_sha256}
    with Path(a.out).open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k!='excluded_p_j'}))


if __name__=='__main__':main()
