"""Own auxiliary roles; formal vectors never enter numeric P caches."""
from copy import deepcopy
from deps20 import collection19,check_collection19,known_checks


def prepare(original,rules,helper,event,capability=None,pool=None):
    value=collection19.prepare(original,rules,helper,event,capability,pool)
    meter=value.meter
    def metadata():
        definitions=[]if rules['program_id']!='formalpair16'else deepcopy(pool['definitions'])
        meter.other['formal_prepared_definition_coefficients_copied']+=sum(len(v['old_coefficients'])for v in definitions)
        return definitions
    value['formal_definitions']=meter.stage('owned_formal_definition_metadata',metadata)
    value['auxiliary_role']=rules['program_id'];value['phases']=list(meter.phases);value['counters']=meter.counters()
    return value


def check(original,rules,helper,actual,pool=None):
    value=check_collection19.preparation(original,rules,helper,actual,pool)
    expected=[]if rules['program_id']!='formalpair16'else pool['definitions']
    if actual['auxiliary_role']!=rules['program_id']or actual['formal_definitions']!=expected:raise ValueError('formal preparation role/definition mismatch')
    # The inherited preparation checker reconstructs numeric initial knowledge
    # solely from own prerequisite/helper constructors, never from a definition.
    known_checks.phase_counts(actual)
    return dict(value,formal_definitions=len(expected),formal_vectors_are_not_numeric_labels=True)
