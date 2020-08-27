import unittest
from librec_auto.core.util import var


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.vcoll = var.VarColl()
        self.vcoll.add_var('librec', 'path1', [10, 20, 30])
        self.vcoll.add_var('librec', 'path2', [0.01, 0.02])
        self.vcoll.add_var('rerank', 'path3', [0.3, 0.6, 0.9])
        self.vcoll.compute_var_configurations()

    def test_factors(self):
        self.assertEqual(self.vcoll.type_factor['librec'], 6)
        self.assertEqual(self.vcoll.type_factor['rerank'], 3)

    def test_get_vars(self):
        vars = self.vcoll.get_vars('rerank')
        self.assertEqual(len(vars), 1)
        vars = self.vcoll.get_vars('librec')
        self.assertEqual(len(vars), 2)
        self.assertEqual(vars[0].path, 'path1')
        self.assertEqual(len(vars[0].val), 3)

    def test_flatten(self):
        var = self.vcoll.get_vars('rerank')[0]
        flat = var.flatten()
        self.assertEqual(flat[0].val, 0.3)

    def test_type_conf(self):
        confs = self.vcoll.get_type_conf('librec')
        self.assertEqual(len(confs), 6)
        conf = confs[0]
        self.assertEqual(type(conf), var.VarConfig)
        self.assertEqual(len(conf.vars), 2)
        self.assertEqual(conf.vars[1].val, 10)

    def test_combine(self):
        vars = self.vcoll.var_confs
        self.assertEqual(len(vars), 18)
        v0 = vars[0]
        self.assertEqual(type(v0), var.VarConfig)
        self.assertEqual(v0.base_config, None)
        self.assertEqual(v0.vars[1].path, 'path1')
        self.assertEqual(v0.vars[1].val, 10)
        self.assertEqual(v0.vars[2].path, 'path3')
        self.assertEqual(v0.vars[2].val, 0.3)
        v13 = vars[13]
        self.assertEqual(type(v13), var.VarConfig)
        self.assertEqual(v13.base_config, vars[1])
        self.assertEqual(v13.vars[1].path, 'path1')
        self.assertEqual(v13.vars[1].val, 20)
        self.assertEqual(v13.vars[2].path, 'path3')
        self.assertEqual(v13.vars[2].val, 0.9)


if __name__ == '__main__':
    unittest.main()
