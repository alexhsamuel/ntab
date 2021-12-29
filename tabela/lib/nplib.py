import numpy as np

#-------------------------------------------------------------------------------

def same(a0, a1):
    if (a0.dtype != a1.dtype or a0.shape != a1.shape):
        return False
    match a0.dtype.kind:
        case "f":
            return ((a0 == a1) | (np.isnan(a0) & np.isnan(a1))).all()
        case "m" | "M":
            return ((a0 == a1) | (np.isnan(a0) & np.isnat(a1))).all()
        case _:
            return (a0 == a1).all()


