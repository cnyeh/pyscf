#!/usr/bin/env python
# Copyright 2014-2020 The PySCF Developers. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors: Chia-Nan Yeh <yehcanon@gmail.com>
#

import unittest
import numpy as np

from pyscf import lib
from pyscf.pbc import gto as gto
from pyscf.pbc import dft as dft

cell = gto.Cell()
cell.unit = 'A'
cell.atom = 'C 0.,  0.,  0.; C 0.8917,  0.8917,  0.8917'
cell.a = '''0.      1.7834  1.7834
            1.7834  0.      1.7834
            1.7834  1.7834  0.    '''

cell.basis = 'gth-dzvp'
cell.pseudo = 'gth-pade'
cell.verbose = 0
cell.build()
kmesh = [2, 1, 1]
kpts = cell.make_kpts(kmesh, wrap_around=True)


H_cell = gto.Cell()
H_cell.build(unit = 'B',
           a = np.eye(3)*4,
           mesh = [11]*3,
           atom = 'H 0 0 0; H 0 0 1.8',
           verbose = 0,
           basis='sto3g')
H_kpts = H_cell.make_kpts([2,1,1], wrap_around=True)

alle_cell = gto.Cell()
alle_cell.unit = 'A'
alle_cell.atom = 'C 0.,  0.,  0.; C 0.8917,  0.8917,  0.8917'
alle_cell.a = '''0.      1.7834  1.7834
            1.7834  0.      1.7834
            1.7834  1.7834  0.    '''

alle_cell.basis = 'sto-3g'
alle_cell.verbose = 0
alle_cell.build()
kmesh = [2, 1, 1]
alle_kpts = alle_cell.make_kpts(kmesh, wrap_around=True)

class KnownValues(unittest.TestCase):
    def test_KGKS(self):
        # In the absence of off diagonal blcoks in the spin space, dft.KGKS should reprocduce the dft.KRKS results

        # Reference from dft.KRKS
        mf = dft.KRKS(cell, kpts)
        mf.xc = 'lda'
        mf.conv_tol = 1e-10
        e_ref = mf.kernel() # -10.38125412115097
        print("e_ref: {}".format(e_ref))
        mf = dft.KGKS(cell, kpts)
        mf.xc = 'lda'
        mf.conv_tol = 1e-10
        e_kgks = mf.kernel()
        print("e_kgks: {}".format(e_kgks))
        self.assertAlmostEqual(e_kgks, e_ref, 8)
    # FIXME Tests below take too much time. A better example is needed.
    def test_KGKS_sfx2c1e(self):
        with lib.light_speed(10) as c:
          mf = dft.KGKS(alle_cell, alle_kpts).density_fit().sfx2c1e()
          mf.with_x2c.approx = 'NONE'
          mf.xc = 'lda'
          mf.conv_tol = 1e-10
          e_kgks = mf.kernel()
          self.assertAlmostEqual(e_kgks, -75.67071562222077, 7)

    def test_KGKS_x2c1e(self):
        with lib.light_speed(10) as c:
          mf = dft.KGKS(alle_cell, alle_kpts).density_fit().x2c1e()
          mf.with_x2c.approx = 'NONE'
          mf.xc = 'lda'
          mf.conv_tol = 1e-10
          e_kgks = mf.kernel()
          self.assertAlmostEqual(e_kgks, -75.66883793093882, 7)
 

if __name__ == '__main__':
    print("Full Tests for pbc.dft.kgks")
    unittest.main()
