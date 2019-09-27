import numpy as np
import rpy2.robjects.packages as rpackages
import pandas as pd

from rpy2 import robjects
from typing import Sequence

from epysurv.simulation.utils import r_list_to_frame, add_date_time_index_to_frame

surveillance = rpackages.importr("surveillance")


def simulate_outbreaks(
    state_weight: float,
    p=0.99,
    r=0.01,
    length=100,
    amplitude=1,
    alpha=1,
    beta=0,
    phi=0,
    frequency=1,
    state: Sequence[int] = None,
) -> pd.DataFrame:
    """Simulation of epidemics which were introduced by point sources.

    The basis of this programme is
    a combination of a Hidden Markov Model (to get random timepoints for outbreaks) and a simple
    model (compare seasonal_noise.py) to simulate the baseline.

    Attributes
    ----------
    p
        probability to get a new outbreak at time i if there was one at time i-1, default 0.99.
    r
        probability to get no new outbreak at time i if there was none at time i-1, default 0.01.
    length
        number of weeks to model, default 100. length is ignored if state is given. In this case the length of state is
        used.
    amplitude
        amplitude (range of sinus), default = 1.
    alpha
        parameter to move along the y-axis (negative values not allowed) with alpha >= A, default = 1.
    beta
        regression coefficient, default = 0.
    phi
        factor to create seasonal moves (moves the curve along the x-axis), default = 0.
    frequency
        factor to determine the oscillation-frequency, default = 1.
    state
        use a state chain to define the status at this timepoint (outbreak or not).  If not given a Markov chain is
        generated by the programme, default NULL.
    state_weight
        additional weight for an outbreak which influences the distribution parameter mu, default = 0.

    Returns
    -------
    A DataFrame of an epidemic time series that contains n weeks where n=``length``.
    The DataFrame is divided into timesteps where each step is equivalent to one calender week.
    It contains a mean value which is the mean case count according to the sinus based model.
    And finally, it contains a column ``n_cases`` that consists of the generates case counts
    based on the sinus model
    """
    simulated = surveillance.sim_pointSource(
        p=p,
        r=r,
        length=length,
        A=amplitude,
        alpha=alpha,
        beta=beta,
        phi=phi,
        frequency=frequency,
        state=robjects.NULL if state is None else robjects.IntVector(state),
        K=state_weight,
    )
    simulated = r_list_to_frame(simulated, ["observed", "state"])
    simulated = add_date_time_index_to_frame(simulated)
    simulated = simulated.rename(
        columns={"observed": "raw_cases", "state": "is_outbreak"}
    )
    simulated["n_outbreak_cases"] = simulated["raw_cases"] * simulated["is_outbreak"]
    return simulated
