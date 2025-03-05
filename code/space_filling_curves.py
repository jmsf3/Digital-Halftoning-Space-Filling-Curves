#! /usr/bin/env python3
# --------------------------------------------------------------------------------------------------
# Space Filling Curves
# --------------------------------------------------------------------------------------------------
# usage examples:
#
# space_filling_curves.py -t peano -o 1
# space_filling_curves.py -t hilbert -o 2
# space_filling_curves.py -t sierpinski -o 3
# --------------------------------------------------------------------------------------------------
# usage: space_filling_curves.py [-h] [-t curve_type] [-o order]
#
# options:
#   -h, --help                              show this help message and exit
#   -t curve_type, --curve_type curve_type  type of space filling curve (hilbert, peano, sierpinski)
#   -o order, --order order                 order of the space filling curve (1, 2, 3, ...)
# --------------------------------------------------------------------------------------------------

import argparse
import numpy as np
import matplotlib.pyplot as plt


def peano(i, order):
    """
    Compute the (x, y) coordinates of the i-th point on a Peano curve of a given order.

    Parameters:
    -----------
    i : int
        The index of the point on the Peano curve.
    order : int
        The order of the Peano curve. The curve will cover a 3^order x 3^order grid.

    Returns:
    --------
    (x, y) : tuple of int
        The (x, y) coordinates of the i-th point on the Peano curve.
    """

    # TODO Implement Peano curve

    return (0, 0)


def hilbert(i, order):
    """
    Compute the (x, y) coordinates of the i-th point on a Hilbert curve of a given order.

    Reference: https://thecodingtrain.com/challenges/c3-hilbert-curve

    Parameters:
    -----------
    i : int
        The index of the point on the Hilbert curve.
    order : int
        The order of the Hilbert curve. The curve will cover a 2^order x 2^order grid.

    Returns:
    --------
    (x, y) : tuple of int
        The (x, y) coordinates of the i-th point on the Hilbert curve.
    """

    first_order_coordinates = [
        (0, 0),
        (0, 1),
        (1, 1),
        (1, 0),
    ]

    quadrant = i & 3
    x, y = first_order_coordinates[quadrant]

    for j in range(1, order):
        i = i >> 2

        shift = 2**j
        quadrant = i & 3

        if (quadrant == 0):
            x, y = y, x
        elif (quadrant == 1):
            x, y = x, y + shift
        elif (quadrant == 2):
            x, y = x + shift, y + shift
        elif (quadrant == 3):
            x, y = 2 * shift - 1 - y, shift - 1 - x

    return (x, y)


def sierpinski(i, order):
    """
    Compute the (x, y) coordinates of the i-th point on a Sierpinski curve of a given order.

    Parameters:
    -----------
    i : int
        The index of the point on the Sierpinski curve.
    order : int
        The order of the Sierpinski curve.  The curve will cover a 4^order x 4^order grid.

    Returns:
    --------
    (x, y) : tuple of int
        The (x, y) coordinates of the i-th point on the Sierpinski curve.
    """

    # TODO Implement Sierpinski curve

    return (0, 0)


def space_filling_curve(curve_type, order):
    """
    Compute the (x, y) coordinates of the points on a space filling curve of a given type and order.

    Parameters:
    -----------
    curve_type : str
        The type of space filling curve (hilbert, peano, sierpinski).
    order : int
        The order of the space filling curve.

    Returns:
    --------
    space_filling_curve : list of tuple of int
        The (x, y) coordinates of the points on the space filling curve.
    """

    if curve_type == 'hilbert':
        n = 2**order
        space_filling_curve = [hilbert(i, order) for i in range(n * n)]
    elif curve_type == 'peano':
        n = 3**order
        space_filling_curve = [peano(i, order) for i in range(n * n)]
    elif curve_type == 'sierpinski':
        n = 4**order
        space_filling_curve = [sierpinski(i, order) for i in range(n * n)]
    else:
        raise ValueError('invalid curve type, choose from (hilbert, peano, sierpinski)')

    return space_filling_curve


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    default = {
        'curve_type': 'hilbert',
        'order': 1,
    }

    parser.add_argument('-t', '--curve_type', metavar='curve_type', type=str,
                        default=default['curve_type'],
                        help='type of space filling curve (hilbert, peano, sierpinski)')
    parser.add_argument('-o', '--order', metavar='order', type=int,
                        default=default['order'],
                        help='order of the space filling curve (1, 2, 3, ...)')
    args = parser.parse_args()

    curve_type = args.curve_type
    order = args.order

    curve = space_filling_curve(curve_type, order)
    n = np.sqrt(len(curve)).astype(int)

    x = [x + 0.5 for x, y in curve]
    y = [y + 0.5 for x, y in curve]

    fig, ax = plt.subplots()
    ax.plot(x, y)

    ax.set_xticks(range(n + 1))
    ax.set_yticks(range(n + 1))

    ax.set_xticklabels([])
    ax.set_yticklabels([])

    ax.set_xlim(0, n)
    ax.set_ylim(0, n)
    ax.set_aspect('equal')

    plt.grid(True)
    plt.title(f'{curve_type.capitalize()} Curve of Order {order}')

    plt.show()
