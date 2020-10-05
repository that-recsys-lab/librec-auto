import itertools
from collections import defaultdict
import copy


# type_factor stores the product of the counts of the values for that type of variable.
# The product of all of the type factors is the total number of experiments. The
# type_factor for the "librec" type gives the number of calls to LibRec.
class VarColl:
    def __init__(self):
        self.vars = defaultdict(list)
        self.var_confs = []
        self.types = []
        self.type_factor = defaultdict(lambda: 1)

    def compute_var_configurations(self):
        if len(self.types) == 0:
            self.var_confs = [VarConfig('merged')]
            return
        # Need to reverse so that the cartesian product has the right priority
        rev_types = copy.copy(self.types)
        rev_types.reverse()
        configs = [self.get_type_conf(type) for type in rev_types]
        conf_product = list(itertools.product(*configs))
        self.var_confs = [
            self.conf_merge(conf_elem) for conf_elem in conf_product
        ]
        self.set_refs()

    def add_var(self, type, path, vals):
        if len(self.vars[type]) == 0:
            self.types.append(type)
        self.vars[type].append(VarInfo(type, path, vals))
        self.type_factor[type] = self.type_factor[type] * len(vals)

    def get_vars(self, type):
        return self.vars[type]

    def get_type_conf(self, type):
        vars = self.get_vars(type)
        flat_vars = [var.flatten() for var in vars]
        flat_vars.reverse()
        var_confs = list(itertools.product(*flat_vars))
        return [VarConfig(type, var_conf) for var_conf in var_confs]

    def conf_merge(self, confs):
        if len(confs) == 1:
            confs[0].type = 'merged'
            return confs[0]
        base = copy.deepcopy(confs[0])
        for conf in confs[1:]:
            base.merge(conf)
        base.type = 'merged'
        # print(str(base.vars))
        return base

    def set_refs(self):
        librec_factor = self.type_factor['librec']
        for i in range(0, len(self.var_confs)):
            row = i // librec_factor
            col = i % librec_factor
            if row > 0:
                self.var_confs[i].ref_config = self.var_confs[col]


class VarConfig:
    def __init__(self, type, vars=()):
        self.exp_no = None
        self.exp_dir = None
        self.type = type
        self.vars = vars
        self.ref_config = None

    def __str__(self):
        return f'<VarConfig {self.type} Vars: {self.vars}'

    def merge(self, vconf):
        self.vars = vconf.vars + self.vars


class VarInfo:
    def __init__(self, type, path, vals):
        self.type = type
        self.path = path
        self.val = vals

    def __str__(self):
        return f'<VarInfo {self.type} {self.path} V: {self.val}>'

    def __repr__(self):
        return self.__str__()

    def flatten(self):
        if type(self.val) is list:
            return [VarInfo(self.type, self.path, val) for val in self.val]
        else:
            return self
