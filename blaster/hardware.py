"""The logic to handle the blaster hardware.
"""

import digitalio
import board
import neopixel

from . import LOGGER

PROPMAKER_PWR = board.D10
PROPMAKER_SWITCH = board.D9
LED_PIN = board.D5
NUM_LEDS = 15
MAX_BRIGHTNESS = 1 / 3
PIXEL_ORDER = neopixel.GRBW


class BlasterProp:
    """Contains the settings and program logic specific to the hardware
    components.
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

        # Initialize the LED strips
        self.leds = neopixel.NeoPixel(LED_PIN, NUM_LEDS,
                                      brightness=MAX_BRIGHTNESS,
                                      pixel_order=PIXEL_ORDER)
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
        target_bounds = range(len(self.leds))
        target_start = offset - len(sprite)

        for i in range(len(sprite)):
            target_index = target_start + i
            if target_index in target_bounds:
                self.leds[target_index] = sprite[i]

    def animate_sprite(self, sprite):
        """Animates a sprite along the LED strip.

        The sprite will begin at the lowest index of `led_strip` and move to
        the highest index.

        Parameters
        ----------
        sprite : array-like(tuple(int))
            Sequence of LED colors that represent the "sprite."
        """
        for i in range(len(self.leds) + len(sprite)):
            self.draw_sprite(sprite, i)
            self.leds.show()
