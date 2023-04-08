# SPDX-License-Identifier: MIT

import os
import adafruit_logging as logging


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
# Attempt to get the logging level from the environment, falling back to the
# WARNING level.
LOG_LEVEL = os.getenv('LOG_LEVEL', logging.WARNING)
LOGGER = logging.getLogger('prop')
LOGGER.setLevel(LOG_LEVEL)

# How long to sleep between update checks in the event loop
LOOP_SLEEP = 0.1

# How long to sleep between steps of the LED animations
ANIMATION_SLEEP = 0.005

# How long the trigger should be held down (in seconds) to enter the CHARGING
# state. If it is held less time than this, it will enter the TRIGGER state.
CHARGE_THRESHOLD = 0.5

# The maximum brightness to allow for the NeoPixel strip as a percentage of the
# strip's full brightness.
MAX_BRIGHTNESS = 0.5

# -----------------------------------------------------------------------------
# Color scheme
# -----------------------------------------------------------------------------
IDLE_FULL = (0, 68, 255, 0)  # Bright ice blue
IDLE_FADE = (0, 11, 42, 0)  # Dark blue
CHARGE_FADE = (0, 22, 64, 0)  # Medium blue
BLAST_FULL = (255, 0, 0, 0)  # Bright red
BLAST_FADE = (25, 0, 0, 0)  # Dark red

# -----------------------------------------------------------------------------
# Sound scheme
# -----------------------------------------------------------------------------
SOUND_DIR = 'sounds'
BLAST_SOUND = f'{SOUND_DIR}/laserShoot.wav'


def apply_brightness(brightness, *pixels):
    """Adjust one or more pixels to a given brightness.

    Parameters
    ----------
    brightness : float
        A value between 0.0 and 1.0, inclusive.
    *pixels : array_like(int)
        One or more pixels.

    Returns
    -------
    array_like(int) | array_like(array_like(int))
        If only a single pixel was provided, a single pixel adjusted to the
        given brightness is returned. If multiple pixels were given, a sequence
        of pixels adjusted to the given brightness is returned.
    """
    brightness = min(max(brightness, 0.0), 1.0)
    result = [
        tuple([int(color * brightness) for color in pixel])
        for pixel in pixels
    ]

    return result[0] if len(result) == 1 else tuple(result)


def grbw(*pixels):
    """Converts one or more RGBW pixels to GRBW.

    Parameters
    ----------
    pixel : array_like(int)
        A sequence of pixels.

    Returns
    -------
    array_like(int) | array_like(array_like(int))
        If only a single pixel was provided, a single converted pixel is
        returned. If multiple pixels were given, a sequence of converted pixels
        is returned.
    """
    result = [(pixel[1], pixel[0], pixel[2], pixel[3]) for pixel in pixels]

    return result[0] if len(result) == 1 else tuple(result)


def pixels_to_bytes(pixels):
    """Converts a sequence of pixels into a byte array.

    Parameters
    ----------
    pixels : array_like(array_like(int))
        A sequence of pixels.

    Returns
    array_like(byte)
        A one-dimensional byte array containing the color components of each
        pixel.
    """
    return bytearray([channel for pixel in pixels for channel in pixel])
