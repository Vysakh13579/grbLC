import inspect
from typing import Callable
from typing import Dict
from typing import List

import numpy as np


def chisq(x, y, sigma, model, p, return_reduced=False):
    r"""A function to calculate the chi-squared value of a given proposed solution:

    .. math:: \chi^2 = \sum_{i=1}^N \frac{(y_i - f(x_i))^2}{\sigma_i^2}

    The reduced :math:`\chi^2` value, :math:`\chi^2_\nu`, can also be returned, and is calculated as:

    .. math:: \chi^2_\nu = \frac{\chi^2}{{\rm \# ~data~ points} - {\rm \# ~free~ params}}

    Parameters
    ----------
    x, y : array_like
        The x and y values of the data points.
    sigma : array_like
        Standard error of the data points.
    model : callable
        The model to be fit to the data. Should take the form of a function that takes `x`, parameters `p`, and returns `y` in the form of ``y = model(x, *p)``.
    p : array_like
        List of parameter values to be used in the model.
    return_reduced : bool, optional
        Determines whether the reduced :math:`\chi^2` will be returned as well, by default False

    Returns
    -------
    numpy.ndarray
        :math:`\chi^2` for each point in the dataset, along with the reduced $\chi^2$ value (if return_reduced=True)
    """

    x = np.asarray(x)
    y = np.asarray(y)
    sigma = np.asarray(sigma)
    r = y - model(x, *p)
    _chisq = np.sum(r ** 2 / sigma ** 2)

    if return_reduced:
        return _chisq, _chisq / (len(x) - len(p))
    else:
        return _chisq


# The famous Willingale et. al 2007 model
# modified so T and F are logarithmic inputs
# to avoid numerical overflow issues
def _w07(x, T, F, alpha, t):

    before = lambda x: (
        -t * 10 ** (-x) + alpha - alpha * 10 ** (x - T) + F * np.log(10)
    ) / np.log(10)

    after = lambda x: F + T * alpha - x * alpha - t * 10 ** (-x) / np.log(10)

    vals = np.piecewise(x, [x < T, x >= T], [before, after])
    return vals


def _simple_bpl(x, T, F, alpha1, alpha2):

    linT, linF = np.power(10, [T, F], dtype=float)
    linX = np.power(10, x, dtype=float)

    before = lambda x: linF * (x / linT) ** (-alpha1)
    after = lambda x: linF * (x / linT) ** (-alpha2)
    vals = np.piecewise(linX, [linX < linT, linX >= linT], [before, after])

    return np.log10(vals)


def _smooth_bpl(x, T, F, alpha1, alpha2, S):

    linT, linF = np.power(10, [T, F], dtype=float)
    linX = np.power(10, x, dtype=float)
    return np.log10(
        linF * ((linX / linT) ** (S * alpha1) + (linX / linT) ** (S * alpha2)) ** (-1 / S)
    )


class Parameter:
    def __init__(
        self,
        name: str,
        description: str = None,
        min: float = -np.inf,
        max: float = np.inf,
        vary: bool = True,
        plot_fmt: str = None,
    ):
        """Parameter class for use with the :class:`Model` class.
                This class is used to store the information about a parameter in a model.
                Information includes the name, description, parameter priors, and whether
                the parameter is to be varied in fitting.

        Parameters
        ----------
        name : str
            Parameter name.
        description : str, optional
            Description of the parameter, by default None
        min : float, optional
            Minimum possible value of the parameter, by default ``-np.inf``
        max : float, optional
            Maximum possible value of the parameter, by default ``np.inf``
        vary : bool, optional
            Controls whether the variable will be allowed to vary in fitting, by default True
        plot_fmt : str, optional
            LaTeX form of the parameter name to be plotted, by default the same as `name`.
        """
        self.name = name
        self.description = (
            description
            if description is not None
            else "Autogenerated argument from input function."
        )
        self.plot_fmt = plot_fmt if plot_fmt is not None else name
        self.min = min
        self.max = max
        self.vary = vary


class Model:
    def __init__(
        self,
        func: Callable,
        name: str = "",
        slug: str = "",
        func_args: List[Parameter] = None,
        bounds: list = None,
    ):
        """Model class for use with the :class:`Lightcurve` class.
                This class is a wrapper around a function that can be used to fit a lightcurve.

        Parameters
        ----------
        func : Callable
            Function to fit to.
        name : str, optional
            Name to the function, by default the variable name of `func`
        slug : str, optional
            The shortened and simplified name of the function, by default `name`
        func_args : Dict[str, Parameter], optional
            Function arguments in the form of a list of :class:`Parameter`, by default None
        bounds : list, optional
            Bounds by which `x` may be varied in fitting, by default ``[-np.inf, np.inf, -np.inf, np.inf]``

        Raises
        ------
        ValueError
            Makes sure all parameter names in `func_args` are actual
            parameters to the function.
        """
        self.__func = func

        self.name = name if name else func.__name__
        self.slug = slug if slug else self.name
        func_argspec = np.asarray(inspect.getfullargspec(func).args[1:], dtype=str)
        if func_args is not None:
            # make sure that each value of in func_args is in func_argspec
            for p in func_args:
                if p.name not in func_argspec:
                    raise ValueError(
                        f"{p.name} is not a valid argument for the {self.name} model. Expected one of {func_argspec}."
                    )

            self.__func_args = {p.name: p for p in func_args}

        else:
            # we assume 1 independent variable, and give blanket bounds to each param
            self.__func_args = {
                name: Parameter(name) for name in inspect.getargspec(func).args[1:]
            }

        # xy bounds
        if bounds is not None:
            assert len(bounds) == 4, "bounds must be a list of length 4"
            self.bounds = bounds
        else:
            self.bounds = [-np.inf, np.inf, -np.inf, np.inf]  # blanket bounds

    def __call__(self, x: np.ndarray, *p, **kwargs):
        return self.func(x, *p[: len(self)], **kwargs)

    def __getitem__(self, key):
        return self.func_args[key]

    def __iter__(self):
        return iter(self.func_args)

    def __len__(self):
        return len(self.func_args)

    def __repr__(self) -> str:
        return f"<grbLC> Model({self.name})"

    @property
    def func(self) -> Callable:
        return self.__func

    @property
    def func_args(self) -> Dict[str, Parameter]:
        return self.__func_args

    def __call__(self, x: np.ndarray, *p, **kwargs):
        return self.func(x, *p[: len(self)], **kwargs)

    def __getitem__(self, key):
        return self.func_args[key]

    def __iter__(self):
        return iter(self.func_args)

    def __len__(self):
        return len(self.func_args)

    def __repr__(self) -> str:
        return f"<grbLC> Model({self.name})"

    @classmethod
    def W07(cls, vary_t=True):
        r"""Willingale et al. (2007) model
            This is a phenomenological model for GRB lightcurve afterglows
            popularized in the paper by Willingale et. al, (2007). [#w07]_

            Taken from his paper, it is as follows:

            $$f(t) = \left \{ \begin{array}{ll}\displaystyle{F_i \exp{\left ( \alpha_i \left( 1 - \frac{t}{T_i} \right) \right )} \exp{\left (- \frac{t_i}{t} \right )}} & {\rm for} \ \ t < T_i \\ ~ & ~ \\ \displaystyle{F_i \left ( \frac{t}{T_i} \right )^{-\alpha_i} \exp{\left ( - \frac{t_i}{t} \right )}} & {\rm for} \ \ t \ge T_i, \\\end{array} \right .$$

            where the transition from the exponential to the power law occurs at the
            point ($T_i$, $F_i$), $\alpha$ determines the temporal decay index of the
            power law, and $t_i$ is the time of the initial rise of the lightcurve.

            As implemented, log space is used for the time (sec) and flux
            (erg cm$^{-2}$ s$^{-1}$). This means that for a light curve in which the
            afterglow plateau phase ends at 10,000 seconds corresponds to a $T_i$ of 5.

            Pre-defined priors on these parameters are:
                * $T_i$ : Uniform(1e-10, 10)
                * $F_i$ : Uniform(-20, 2)
                * $\alpha$ : Uniform(0, 5)
                * $t$ : Uniform(0, inf)

        Parameters
        ----------
        vary_t : bool, optional
            The fourth parameter to this :py:class:`Model`, `t`, often does not vary
            the lightcurve in any way and thus is sometimes set to zero. This allows
            the user to make the fitter not vary it. Otherwise, you can set the vary
            parameter to zero via ``Model[Parameter.name].vary = False``. By default True.

        Returns
        -------
        :class:`Model`
            The Willingale et al. (2007) model.


        An example lightcurve is shown below:

        .. jupyter-execute::

            import matplotlib.pyplot as plt
            import numpy as np
            import grblc
            %matplotlib inline

            w07 = grblc.Model.W07()
            x = np.linspace(2, 8, 100)
            T, F, alpha, t = 5, -12, 1.5, 1
            y = w07(x, T, F, alpha, t)
            plt.plot(x, y)
            plt.title(w07.name)
            plt.xlabel("log Time (s)")
            plt.ylabel("log Flux (erg cm$^{-2}$ s$^{-1}$)")
            plt.show()


        .. [#w07] https://arxiv.org/abs/astro-ph/0612031
        """
        return cls(
            name="Willingale 2007",
            slug="w07",
            func=_w07,
            func_args=[
                Parameter(
                    "T",
                    "log time at end of plateau (log sec)",
                    min=1e-10,
                    max=10,
                ),
                Parameter(
                    "F",
                    "log flux at end of plateau (log erg/cm^2/s)",
                    min=-20,
                    max=2,
                ),
                Parameter(
                    "alpha",
                    "temporal decay index of power law",
                    plot_fmt=r"$\alpha$",
                    min=0,
                    max=5,
                ),
                Parameter(
                    "t",
                    "log time at peak (log sec)",
                    min=0,
                    max=np.inf,
                    vary=vary_t,
                ),
            ],
        )

    @classmethod
    def SMOOTH_BPL(cls):
        r"""Smooth broken power law model
            This is an empirical piece-wise model for GRB lightcurve afterglows.

            The function is as follows:

            $$f(t) = F_i \left (\left (\frac{t}{T_i} \right )^{S\alpha_1} + \left (\frac{t}{T_i} \right )^{S \alpha_2} \right )^{-\frac{1}{S}}$$

            where the transition from the exponential to the power law occurs at the
            point ($T_i$, $F_i$), $\alpha_1$ determines the temporal decay index of
            the initial power law, and $\alpha_2$ is the temporal decay index of the
            final power law, and $S$ is the smoothing factor.

            As implemented, log space is used for the time (sec) and flux
            (erg cm$^{-2}$ s$^{-1}$). This means that for a light curve in which the
            afterglow plateau phase ends at 10,000 seconds corresponds to a $T_i$ of 5.

            Pre-defined priors on these parameters are::
                * $T_i$ : Uniform(1e-10, 10)
                * $F_i$ : Uniform(-20, 2)
                * $\alpha_1$ : Uniform(-5, 5)
                * $\alpha_2$ : Uniform(-5, 5)
                * $S$ : Uniform(-inf, inf)

        Returns
        -------
        :class:`Model`
            The simple broken power law model.


        An example lightcurve is shown below:

        .. jupyter-execute::

            import matplotlib.pyplot as plt
            import numpy as np
            import grblc
            %matplotlib inline

            sbpl = grblc.Model.SMOOTH_BPL()
            x = np.linspace(2, 8, 100)
            T, F, alpha1, alpha2, S = p = 5, -12, -0.1, 1.5, 0.5
            y = sbpl(x, *p)
            plt.plot(x, y)
            plt.title(sbpl.name)
            plt.xlabel("log Time (s)")
            plt.ylabel("log Flux (erg cm$^{-2}$ s$^{-1}$)")
            plt.show()


        """
        return cls(
            name="smooth broken power law",
            slug="smooth_bpl",
            func=_smooth_bpl,
            func_args=[
                Parameter(
                    "T",
                    "log time at end of plateau (log sec)",
                    min=1e-5,
                    max=10,
                ),
                Parameter(
                    "F",
                    "log flux at end of plateau  (log erg cm^-2 s^-1)",
                    min=-20,
                    max=-2,
                ),
                Parameter(
                    "alpha1",
                    "temporal decay index of initial power law",
                    min=-5,
                    max=5,
                    plot_fmt=r"$\alpha_1$",
                ),
                Parameter(
                    "alpha2",
                    "temporal decay index of end power law",
                    min=0,
                    max=20,
                    plot_fmt=r"$\alpha_2$",
                ),
                Parameter("S", "smoothing factor"),
            ],
        )

    @classmethod
    def SIMPLE_BPL(cls):
        r"""Simple broken power law model
            This is an empirical piece-wise model for GRB lightcurve afterglows.

            The function is as follows:

            $$f(t) = \left \{ \begin{array}{ll} \displaystyle{F_i \left (\frac{t}{T_i} \right)^{-\alpha_1} } & {\rm for} \ \ t < T_i \\ \displaystyle{F_i \left ( \frac{t}{T_i} \right )^{-\alpha_2} } & {\rm for} \ \ t \ge T_i, \\ \end{array} \right . $$

            where the transition from the exponential to the power law occurs at the point
            ($T_i$, $F_i$), $\alpha_1$ determines the temporal decay index of the initial
            power law, and $\alpha_2$ is the temporal decay index of the final power law.

            As implemented, log space is used for the time (sec) and flux
            (erg cm$^{-2}$ s$^{-1}$). This means that for a light curve in which the
            afterglow plateau phase ends at 10,000 seconds corresponds to a $T_i$ of 5.

            Pre-defined priors on these parameters are:
                * T : Uniform(1e-10, 10)
                * F : Uniform(-20, 2)
                * $\alpha_1$ : Uniform(-5, 5)
                * $\alpha_2$ : Uniform(-5, 5)

        Returns
        -------
        :class:`Model`
            The simple broken power law model.


        An example lightcurve is shown below:

        .. jupyter-execute::

            import matplotlib.pyplot as plt
            import numpy as np
            import grblc
            %matplotlib inline

            sbpl = grblc.Model.SIMPLE_BPL()
            x = np.linspace(2, 8, 100)
            T, F, alpha1, alpha2 = p = 5, -12, -0.1, 1.5
            y = sbpl(x, *p)
            plt.plot(x, y)
            plt.title(sbpl.name)
            plt.xlabel("log Time (s)")
            plt.ylabel("log Flux (erg cm$^{-2}$ s$^{-1}$)")
            plt.show()


        """
        return cls(
            name="simple broken power law",
            slug="simple_bpl",
            func=_simple_bpl,
            func_args=[
                Parameter(
                    "T",
                    "log time at end of plateau (log sec)",
                    min=1e-5,
                    max=10,
                ),
                Parameter(
                    "F",
                    "log flux at end of plateau  (log erg cm^-2 s^-1)",
                    min=-20,
                    max=-2,
                ),
                Parameter(
                    "alpha1",
                    "temporal decay index of initial power law",
                    min=-5,
                    max=5,
                    plot_fmt=r"$\alpha_1$",
                ),
                Parameter(
                    "alpha2",
                    "temporal decay index of end power law",
                    min=0,
                    max=20,
                    plot_fmt=r"$\alpha_2$",
                ),
            ],
        )
