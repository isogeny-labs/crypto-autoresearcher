"""Fixed study geometry. Reading this module draws no nonce or curve."""
SLOTS = 8
STAGES = ('discovery', 'validation', 'confirmation-A', 'confirmation-B')
TIERS = (10, 13, 16)
FULL = {'setups': 432, 'intents': 73728, 'singles': 691200,
        'traces': 73728, 'cells': 147456}
GEOMETRY = {'domains': 96, 'confirmation_domains': 48, 'targets': 3072,
            'slots_per_stage_tier': 8, 'targets_per_confirmation_domain': 64,
            'blindings_per_target': 8, 'calibration_arms': 8,
            'physical_solver_rows': 2, 'separate_generator_processes': 1}
SAMPLER_LIMITS = {'curve_proposal_limit': 10000,
                  'point_proposal_limit': 1024,
                  'target_proposal_limit': 1024}


def validate_profile(profile):
    expected = {'schema', 'geometry', 'workload', 'stages', 'tiers',
                'cells', 'sampler_limits', 'storage', 'qualification'}
    if type(profile) is not dict or set(profile) != expected:
        raise ValueError('exact v6 source profile fields required')
    if profile['schema'] != 'controlled-followup-v6.study/v1':
        raise ValueError('study schema')
    for field, value in [('geometry', GEOMETRY), ('workload', FULL),
                         ('sampler_limits', SAMPLER_LIMITS)]:
        if profile[field] != value or any(type(v) is not int for v in profile[field].values()):
            raise ValueError('fixed study field differs: ' + field)
    if profile['stages'] != list(STAGES) or profile['tiers'] != list(TIERS):
        raise ValueError('stage/tier law differs')
    if any(type(v) is not str for v in profile['stages']) or any(type(v) is not int for v in profile['tiers']):
        raise ValueError('stage/tier types')
    if profile['cells'] != [[0, 0], [0, 2], [1, 0], [1, 2], [2, 0], [2, 2]]:
        raise ValueError('all six cells must be retained')
    if any(type(v) is not int for pair in profile['cells'] for v in pair):
        raise ValueError('cell integer types')
    if profile['storage'] != {'part_bytes': 134217728, 'max_line_bytes': 67108864,
                              'input_bytes': 268435456, 'file_bytes': 2147483648}:
        raise ValueError('storage policy differs')
    if profile['qualification'] != {'wall_valid': False, 'full_cost_qualified': False,
                                    'primitive_counter_replay_qualified': False}:
        raise ValueError('source preparation grants no measurement qualification')
    if any(type(v) is not bool for v in profile['qualification'].values()):
        raise ValueError('qualification booleans')
    return profile
