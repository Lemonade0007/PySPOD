'''
Base module for the POD:
    - `fit` and `predict` methods must be implemented in inherited classes
'''
from __future__ import division

# Import standard Python packages
import os
import sys
import time
import pickle
import warnings
import scipy
import numpy as np
from pyspod.pod.base import Base
import pyspod.utils.parallel as utils_par
BYTE_TO_GB = 9.3132257461548e-10



## Standard POD class
## ----------------------------------------------------------------------------

class Standard(Base):
    '''
    Class that implements the standard Proper Orthogonal Decomposition.
    '''

    def fit(self, data, nt):
        '''
        Class-specific method to fit the data matrix `data` using standard POD.
        '''
        start = time.time()

        self._pr0(' ')
        self._pr0('Initialize data ...')
        self._initialize(data, nt)

        ## reshape data and remove mean
        d = self._data.reshape(self._nt, self._data[0,...].size)
        d = d - self._t_mean
        d = d.T

        ## eigendecomposition
        Q = d.conj().T @ (d * self._weights)
        Q = utils_par.allreduce(Q, comm=self._comm)
        w, v = scipy.linalg.eig(Q)

        # bases
        self._pr0(' ')
        self._pr0('Calculating standard POD ...')
        st = time.time()
        phi = np.real(d @ v) / np.sqrt(w[:])

        # truncation and save
        phi_r = phi[:,0:self._n_modes_save]
        self._file_modes = os.path.join(self._savedir_sim, 'modes.npy')
        shape = [*self._xshape,self._nv,self._n_modes_save]
        if self._comm: shape[self._maxdim_idx] = -1
        phi_r.shape = shape
        utils_par.npy_save(
            self._comm, self._file_modes, phi_r, axis=self._maxdim_idx)
        self._pr0(f'done. Elapsed time: {time.time() - st} s.')
        self._pr0(f'Modes saved in  {self._file_modes}')
        self._eigs = w
        self._store_and_save()
        return self

## ----------------------------------------------------------------------------
