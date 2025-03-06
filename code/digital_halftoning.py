#! /usr/bin/env python3
# --------------------------------------------------------------------------------------------------
# Digital Halftoning with Space Filling Curves
#
# Implementation of:
#   Digital Halftoning with Space Filling Curves, Luiz Velho and Jonas de Miranda Gomes
#   Special Interest Group on Computer Graphics and Interactive Techniques (SIGGRAPH), 1991
# --------------------------------------------------------------------------------------------------
# usage examples:
#
# digital_halftoning.py -i data/boots.jpg -o data/boots_sierpinski.jpg -t sierpinski -s 6 -d random
# digital_halftoning.py -i data/leafs.jpg -o data/leafs_peano.jpg -t peano -s 8 -d ordered
# digital_halftoning.py -i data/araras.png -o data/araras_peano.png -t peano -s 4 -d standard
# digital_halftoning.py -i data/impa.png -o data/impa_hilbert.png -t hilbert -s 8 -d ordered
# --------------------------------------------------------------------------------------------------
# usage: digital_halftoning.py [-h] [-i image_in] [-o image_out] [-t curve_type] [-s cluster_size]
#                              [-d distribution] [-g gamma] [-b blur] [-w weight]
#
# options:
#   -h, --help                                    show this help message and exit
#   -i image_in, --image_in image_in              path to the input image
#   -o image_out, --image_out image_out           path to the output image
#   -t curve_type, --curve_type curve_type        type of space filling curve
#   -s cluster_size, --cluster_size cluster_size  size of the cluster for halftoning
#   -d distribution, --distribution distribution  within-cluster intensity distribution
#   -g gamma, --gamma gamma                       gamma value for gamma correction
#   -b blur, --blur blur                          blur value for edge enhancement
#   -w weight, --weight weight                    weight value for edge enhancement
# --------------------------------------------------------------------------------------------------

import argparse
import cv2
import numpy as np
from space_filling_curves import space_filling_curve


def order(image_in, curve_type):
    """
    Compute the order of the space-filling curve based on the input image dimensions and curve type.

    Parameters:
    -----------
    image_in : numpy.ndarray
        The input image for which the curve order is to be computed.
    curve_type : str
        The type of space filling curve (hilbert, peano, sierpinski).

    Returns:
    --------
    order : int
        The computed order of the specified space-filling curve.
    """

    if curve_type == 'hilbert':
        return np.ceil(np.log2(max(image_in.shape))).astype(int)
    elif curve_type == 'peano':
        return np.ceil(np.log(max(image_in.shape)) / np.log(3)).astype(int)
    elif curve_type == 'sierpinski':
        return np.ceil(np.log(max(image_in.shape)) / np.log(4)).astype(int)
    else:
        raise ValueError('invalid curve type, choose from (hilbert, peano, sierpinski)')


def gamma_correction(image_in, gamma):
    """
    Apply gamma correction to an input image.

    Parameters:
    -----------
    image_in : numpy.ndarray
        The input image with pixel values in the range [0, 255].
    gamma : float
        The gamma correction value. A gamma value < 1 will lighten the image, while a
        gamma value > 1 will darken the image.

    Returns:
    --------
    gamma_corrected_image : numpy.ndarray
        The gamma-corrected image with pixel values in the range [0, 255].
    """

    normalized_image = image_in / 255.0
    gamma_corrected_image = np.power(normalized_image, gamma)
    gamma_corrected_image = (gamma_corrected_image * 255).astype(np.uint8)
    return gamma_corrected_image


def edge_enhancement(image_in, blur, weight):
    """
    Enhance the edges of an input image using Gaussian blur and weighted addition.

    Parameters:
    -----------
    image_in : numpy.ndarray
        The input image to be edge-enhanced.
    blur : float
        The standard deviation for Gaussian kernel used in blurring.
    weight : float
        The weight factor for combining the original and blurred images.

    Returns:
    --------
    edge_enhanced_image : numpy.ndarray
        The edge-enhanced image.
    """

    blurred_image = cv2.GaussianBlur(image_in, (0, 0), sigmaX=blur)
    edge_enhanced_image = cv2.addWeighted(image_in, 1 + weight, blurred_image, -weight, 0)
    edge_enhanced_image = np.clip(edge_enhanced_image, 0, 255).astype(np.uint8)
    return edge_enhanced_image


def halftoning(image_in, curve_type, cluster_size, distribution):
    """
    Apply digital halftoning to an input image using a specified space-filling curve and
    distribution method.

    Parameters:
    -----------
    image_in : numpy.ndarray
        The input grayscale image to be halftoned.
    curve_type : str
        The type of space filling curve (hilbert, peano, sierpinski).
    cluster_size : int
        The size of the clusters to divide the curve into for processing.
    distribution : str
        The method of distributing pixel intensities within each cluster
        (standard, ordered, or random).

    Returns:
    --------
    halftone : numpy.ndarray
        The resulting halftoned image.
    """

    halftone = np.zeros_like(image_in)

    curve = space_filling_curve(curve_type, order(halftone, curve_type))
    curve = [(x, y) for x, y in curve if x < halftone.shape[1] and y < halftone.shape[0]]

    n_clusters = len(curve) // cluster_size
    clusters = np.array_split(curve, n_clusters)
    intensity_accumulator = 0

    for cluster in clusters:
        if distribution == 'ordered':
            cluster = sorted(cluster, key=lambda p: image_in[p[1], p[0]])
        elif distribution == 'random':
            np.random.shuffle(cluster)
        elif distribution != 'standard':
            raise ValueError('invalid distribution type, choose from (standard, ordered, random)')

        for x, y in cluster:
            intensity_accumulator += image_in[y, x]

        for x, y in cluster:
            if intensity_accumulator >= 255:
                halftone[y, x] = 255
                intensity_accumulator -= 255
            else:
                halftone[y, x] = 0

    return halftone


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    default = {
        'curve_type': 'hilbert',
        'cluster_size': 4,
        'distribution': 'standard',
        'gamma': 1.0,
        'blur': 1.0,
        'weight': 1.0,
    }

    parser.add_argument('-i', '--image_in', metavar='image_in', type=str,
                        help='path to the input image')
    parser.add_argument('-o', '--image_out', metavar='image_out', type=str,
                        help='path to the output image')
    parser.add_argument('-t', '--curve_type', metavar='curve_type', type=str,
                        default=default['curve_type'],
                        help='type of space filling curve (hilbert, peano, sierpinski)')
    parser.add_argument('-s', '--cluster_size', metavar='cluster_size', type=int,
                        default=default['cluster_size'],
                        help='size of the cluster for halftoning')
    parser.add_argument('-d', '--distribution', metavar='distribution', type=str,
                        default=default['distribution'],
                        help='within-cluster intensity distribution (standard, ordered, random)')
    parser.add_argument('-g', '--gamma', metavar='gamma', type=float,
                        default=default['gamma'],
                        help='gamma value for gamma correction')
    parser.add_argument('-b', '--blur', metavar='blur', type=float,
                        default=default['blur'],
                        help='blur value for edge enhancement')
    parser.add_argument('-w', '--weight', metavar='weight', type=float,
                        default=default['weight'],
                        help='weight value for edge enhancement')
    args = parser.parse_args()

    image_in = cv2.imread(args.image_in, cv2.IMREAD_GRAYSCALE)
    curve_type = args.curve_type
    cluster_size = args.cluster_size
    distribution = args.distribution
    gamma = args.gamma
    blur = args.blur
    weight = args.weight

    gamma_corrected_image = gamma_correction(image_in, gamma)
    edge_enhanced_image = edge_enhancement(gamma_corrected_image, blur, weight)
    halftone_image = halftoning(edge_enhanced_image, curve_type, cluster_size, distribution)

    cv2.imwrite(args.image_out, halftone_image)
