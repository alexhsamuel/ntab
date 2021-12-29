import cython

from libc.math cimport isinf, isnan, round
cdef extern from "<math.h>" nogil:
    double pow10(double)


ctypedef fused number:
    cython.char
    cython.double 
    cython.float
    cython.int
    cython.long
    cython.longlong
    cython.short
    cython.uchar
    cython.uint
    cython.ulong
    cython.ulonglong
    cython.ushort


@cython.boundscheck(False)
@cython.wraparound(False)
cpdef analyze(number[:] arr, max_precision=14):
    cdef Py_ssize_t n = arr.shape[0]
    if n == 0:
        raise ValueError("array is empty")

    # FIXME: Make float-specific values conditional.
    cdef cython.int num_zero = 0
    cdef cython.int num_nan = 0
    cdef cython.int num_posinf = 0
    cdef cython.int num_neginf = 0
    cdef cython.int num = 0
    cdef number min = arr[0]
    cdef number max = arr[0]
    cdef number abs_min = abs(arr[0])
    cdef cython.int precision = 0
    cdef cython.double precision_scale = 1

    cdef number x
    cdef number a
    cdef cython.double scaled
    for i in range(n):
        x = arr[i]
        a = abs(x)
        if x == 0:
            num_zero += 1

        if number is float or number is double:
            # Floating point types.
            if isnan(x):
                num_nan += 1
            elif isinf(x):
                if x > 0:
                    num_posinf += 1
                else:
                    num_neginf += 1
            else:
                num += 1
                if x < min:
                    min = x
                if max < x:
                    max = x
                if a != 0 and a < abs_min:
                    abs_min = a

        else:
            # Integral types.
            num += 1
            if x < min:
                min = x
            if max < x:
                max = x
            if a != 0 and a < abs_min:
                abs_min = a

            while precision < max_precision:
                scaled = x * precision_scale
                if abs(round(scaled) - scaled) < 1e-8 * precision_scale:
                    pass
                else:
                    precision += 1
                    precision_scale = pow10(precision)

    return {
        "num"           : num,
        "num_zero"      : num_zero,
        "num_nan"       : num_nan,
        "num_posinf"    : num_posinf,
        "num_neginf"    : num_neginf,
        "min"           : min,
        "max"           : max,
        "abs_min"       : abs_min,
    }


