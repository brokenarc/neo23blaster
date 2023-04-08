# SPDX-License-Identifier: MIT

"""The logic to handle the blaster hardware.
"""

import time
import digitalio
import board
import audioio
import audiocore
from neopixel_write import neopixel_write

from . import ANIMATION_SLEEP, BATTERY_GOOD, BATTERY_WARN, BLAST_FADE, \
    BLAST_FULL, CHARGE_FADE, IDLE_FADE, IDLE_FULL, LOGGER, MAX_BRIGHTNESS, \
    SOUND_DIR, apply_brightness, grbw, pixels_to_bytes

PROPMAKER_PWR = board.D10
PROPMAKER_SWITCH = board.D9
AUDIO_PIN = board.A0
LED_PIN = board.D5
NUM_LEDS = 15
BPP = 4  # bytes per pixel

# -----------------------------------------------------------------------------
# The sprites used by the various states.
#
# The strip used in this build has GRBW byte ordering. For RGBW strips, remove
# the call to grbw
CHARGE_SPRITE = pixels_to_bytes(
    apply_brightness(
        MAX_BRIGHTNESS,
        *grbw(CHARGE_FADE, IDLE_FULL, IDLE_FULL, CHARGE_FADE)
    )
)

BLAST_SPRITE = pixels_to_bytes(
    apply_brightness(
        MAX_BRIGHTNESS,
        *grbw(IDLE_FADE, BLAST_FADE, BLAST_FULL, BLAST_FADE, IDLE_FADE)
    )
)

IDLE_IMAGE = pixels_to_bytes(
    [grbw(apply_brightness(MAX_BRIGHTNESS, IDLE_FADE))] * NUM_LEDS
)

# -----------------------------------------------------------------------------
# The sounds used by the blaster
BLAST_SOUND = f'{SOUND_DIR}/laserShoot.wav'


def play_wav(filename):
    """Plays the given WAV file and returns when it has finished playing.

    Parameters
    ----------
    filename : str
        The full filename of the WAV file to play.
    """
    with audioio.AudioOut(AUDIO_PIN) as audio:  # Speaker connector
        wave_file = open(filename, "rb")
        wave = audiocore.WaveFile(wave_file)

        audio.play(wave)
        while audio.playing:
            pass


class BlasterProp:
    """Contains the settings and program logic specific to the hardware
    components.

    Attributes
    ----------
    propmaker_power : object
        Reference to the Feather M4 GPIO pin that turns on the Prop-Maker.
    switch : object
        Reference to the Feather M4 GPIO pin that connects to the switch
        connection on the Prop-Maker.
    led_pin : object
        Reference to the Feather M4 GPIO pin that connects to the NeoPixels
        connector.
    led_strip : bytearray
        The raw bytes that represent the NeoPixel colors.
    """

    def __init__(self):
        # Set PROPMAKER_PWR high to power NeoPixels/Audio/RGB on the Prop-Maker
        self.propmaker_power = digitalio.DigitalInOut(PROPMAKER_PWR)
        self.propmaker_power.direction = digitalio.Direction.OUTPUT
        self.propmaker_power.value = True

        # Set up the onboard switch. The hardware for the onboard switch is
        # configured with a pull up resistor.
        self.switch = digitalio.DigitalInOut(PROPMAKER_SWITCH)
        self.switch.switch_to_input(pull=digitalio.Pull.UP)

        # Initialize the LED strip
        self.led_pin = digitalio.DigitalInOut(LED_PIN)
        self.led_pin.direction = digitalio.Direction.OUTPUT
        self.led_strip = bytearray(NUM_LEDS * BPP)

        LOGGER.info('Hardware initialization complete')

    @property
    def trigger(self) -> bool:
        """The trigger press state: `True` if the trigger is pressed, `False`
        if it is not."""
        return not self.switch.value

    def draw_sprite(self, sprite, offset):
        """Draws a sprite onto the LED strip

        The sprite is rendered from its maximum index downwards. So with an
        `offset` of `0`, only the color of the sprite's greatest index will be
        visible.

        Parameters
        ----------
        sprite : array-like(tuple(int))
            Sequence of LED colors that represent the "sprite." Index `0` is
            the tail of the sprite and index `length - 1` is the head of the
            sprite. The tail of the sprite needs to be the color the strip
            should return to as the sprite moves past.
        offset : int
            Where along the strip to place the sprite.
        """
        target_bounds = range(len(self.led_strip))
        target_start = offset - len(sprite)

        for i in range(len(sprite)):
            target_index = target_start + i
            if target_index in target_bounds:
                self.led_strip[target_index] = sprite[i]

    def animate_sprite(self, sprite):
        """Animates a sprite along the LED strip.

        The sprite will begin at the lowest index of `led_strip` and move to
        the highest index.

        Parameters
        ----------
        sprite : array-like(tuple(int))
            Sequence of LED colors that represent the "sprite."
        """
        for i in range(0, len(self.led_strip) + len(sprite), BPP):
            self.draw_sprite(sprite, i)
            neopixel_write(self.led_pin, self.led_strip)
            time.sleep(ANIMATION_SLEEP)

    def update_battery(self):
        """Check the current battery voltage level and update the battery
        status LED.
        """
        LOGGER.debug('Checking battery level.')
        voltage = 3.7 # replace with the logic to get the voltage level

        if voltage >= BATTERY_GOOD:
            pass # replace with logic to change battery LED to good
        elif voltage >= BATTERY_WARN:
            pass # replace with logic to change battery LED to warning
        else:
            pass # replace with logic to change battery LED to danger

    def play_idle_effect(self):
        """Displays the idle effect.
        """
        neopixel_write(self.led_pin, IDLE_IMAGE)

    def play_charging_effect(self):
        """Plays the charging effect.
        """
        self.animate_sprite(CHARGE_SPRITE)

    def play_firing_effect(self):
        """Plays the firing effect.
        """
        play_wav(BLAST_SOUND)
        self.animate_sprite(BLAST_SPRITE)
