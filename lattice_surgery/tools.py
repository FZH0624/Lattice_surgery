from collections import namedtuple
from pre_processing import *

LowLevelOpts = namedtuple('LowLevelOpts', 'd, time_cycle, time_single, time_two, physical_error',
                          defaults=(None, None, 1e-7, 1e-6, 1e-3))

Params = namedtuple('Params', 'type, circuit, low_level', defaults=('surface', Circuit([]), LowLevelOpts()))


class PhysicalCost(namedtuple('PhysicalCost', ('p', 't'))):
    """Physical cost of some gates: error probability and runtime.

    Attributs
    ---------
        p : error probability.
        t : runtime.

    Methods
    -------
        Has same interface as namedtuple, except for listed operators.

    Operators
    ---------
        a + b : cost of serial execution of a and b.
        k * a : cost of serial execution of a k times (k can be float).
        a | b : cost of parallel execution of a and b.

    """

    def __add__(self, other):
        """Cost of sequential execution of self and other."""
        if not isinstance(other, __class__):
            return NotImplemented
        return __class__(1 - (1 - self.p) * (1 - other.p), self.t + other.t)

    def __mul__(self, other):
        """
        Cost of sequential execution of self other times.

        Other does not need to be integer (as some gates are probabilistically
                                           applied).
        """
        if not isinstance(other, numbers.Real):
            return NotImplemented
        return __class__(1 - (1 - self.p) ** other, self.t * other)

    def __rmul__(self, other):
        """Right multiplication."""
        return self * other

    def __sub__(self, other):
        """Subtraction: revert previous of future addition."""
        return self + (-1 * other)

    def __or__(self, other):
        """Cost of parallel execution of self and other."""
        if not isinstance(other, __class__):
            return NotImplemented
        return __class__(1 - (1 - self.p) * (1 - other.p), max(self.t, other.t))

    def parrel(self, k):
        if not isinstance(k, int) and k <= 0:
            return NotImplemented
        return __class__(1 - (1 - self.p) ** k, self.t)

    @property
    def exp_t(self):
        """Average runtime (several intents might be required)."""
        if self.p is None:
            return self.t
        if self.p >= 1:
            return float('inf')
        return self.t / (1 - self.p)

    @property
    def exp_t_str(self):
        """Format average runtime."""
        try:
            return timedelta(seconds=self.exp_t)
        except OverflowError:
            if self.exp_t == float('inf'):
                return "∞"
            return str(round(self.exp_t / (3600 * 24 * 365.25))) + " years"

    def __str__(self):
        """Readable representation of a PhysicalCost."""
        # pylint: disable=C0103
        try:
            t = timedelta(seconds=self.t)
        except OverflowError:
            if self.t == float('inf'):
                t = "∞"
            else:
                t = str(round(self.t / (3600 * 24 * 365.25))) + " years"
        return f"PhysicalCost(p={self.p}, t={t}, exp_t={self.exp_t_str})"