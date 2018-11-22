"""
.. module:: test_checkpointing_serial
  :synopsis: Test Checkpointing Serial
.. moduleauthor:: David Eriksson <dme65@cornell.edu>
"""

from pySOT.adaptive_sampling import CandidateSRBF
from pySOT.experimental_design import SymmetricLatinHypercube
from pySOT.strategy import GlobalStrategy
from pySOT.surrogate import RBFInterpolant, CubicKernel, LinearTail
from pySOT.optimization_problems import Ackley
from pySOT.controller import CheckpointController

from poap.controller import SerialController
import numpy as np
import multiprocessing
import time
import os

maxeval = 200

opt_prob = Ackley(dim=10)
print(opt_prob.info)
fname = "checkpoint.pysot"


def test_checkpoint_serial():
    if os.path.isfile(fname):
        os.remove(fname)

    # Run for 3 seconds and kill the controller
    p = multiprocessing.Process(target=init, args=())
    p.start()
    time.sleep(3)
    p.terminate()
    p.join()

    print("Die controller, die!")

    # Resume the run
    resume()


def init():
    print("\nInitializing run...")
    surrogate = RBFInterpolant(
        opt_prob.dim, kernel=CubicKernel(), tail=LinearTail(opt_prob.dim))

    # Create a strategy and a controller
    controller = SerialController(opt_prob.eval)
    controller.strategy = \
        GlobalStrategy(max_evals=maxeval, opt_prob=opt_prob,
                       exp_design=SymmetricLatinHypercube(dim=opt_prob.dim,
                                                          npts=2 * (opt_prob.dim + 1)),
                       surrogate=surrogate,
                       adapt_sampling=CandidateSRBF(data=opt_prob, numcand=100*opt_prob.dim),
                       asynchronous=True, batch_size=1, stopping_criterion=None, extra=None)

    # Wrap controller in checkpoint object
    controller = CheckpointController(controller, fname=fname)
    result = controller.run()
    print('Best value found: {0}'.format(result.value))
    print('Best solution found: {0}\n'.format(
        np.array_str(result.params[0], max_line_width=np.inf,
                     precision=5, suppress_small=True)))


def resume():
    print("Resuming run...\n")
    controller = SerialController(opt_prob.eval)

    # Wrap controller in checkpoint object
    controller = CheckpointController(controller, fname=fname)
    result = controller.resume()
    print('Best value found: {0}'.format(result.value))
    print('Best solution found: {0}\n'.format(
        np.array_str(result.params[0], max_line_width=np.inf,
                     precision=5, suppress_small=True)))


if __name__ == '__main__':
    test_checkpoint_serial()