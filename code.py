import digitalio
import board
import neopixel

# Configuration
PROPMAKER_PWR = board.D10
LED_PIN = board.D5
NUM_LEDS = 15
MAX_BRIGHTNESS = 1 / 3

# Setup colors
IDLE_FULL = (0, 68, 255, 0)
IDLE_FADE = (0, 11, 42, 0)
BLAST_FULL = (255, 0, 0, 0)
BLAST_FADE = (25, 0, 0, 0)

# Create a "sprite" to crawl along the length of the NeoPixel strip. Index 0
# is the tail of the sprite and index length - 1 is the head of the sprite.
# The tail of the sprite needs to be the color the strip should return to as
# the sprite moves past.
BLAST_SPRITE = (IDLE_FADE, BLAST_FADE, BLAST_FULL, BLAST_FADE)


def draw_sprite(led_strip, sprite, offset):
    """
    Draws a sprite onto an LED strip

    The sprite is rendered from its maximum index downwards. So with an
    `offset` of `0`, only the color of the sprite's greatest index will be
    visible. 

    :param Sequence[int, int, int, int] led_strip: LED strip to draw the sprite
           on.
    :param Sequence[int, int, int, int] sprite: Sequence of LED colors that
           represent the "sprite."
    :param int offset: Where along the strip to place the sprite.
    """
    target_bounds = range(len(led_strip))
    target_start = offset - len(sprite)

    for i in range(len(sprite)):
        target_index = target_start + i
        if target_index in target_bounds:
            led_strip[target_index] = sprite[i]


def draw_blast(led_strip, sprite):
    """
    Animates a sprite along an LED strip for a blast effect.

    The sprite will begin at the lowest index of `led_strip` and move to the
    highest index.

    :param Sequence[int, int, int, int] led_strip: LED strip to draw the sprite
           on.
    :param Sequence[int, int, int, int] sprite: Sequence of LED colors that
           represent the "sprite."
    """
    for i in range(len(led_strip) + len(sprite)):
        draw_sprite(led_strip, sprite, i)
        led_strip.show()

# -----------------------------------------------------------------------------
# Prop setup
# -----------------------------------------------------------------------------

# Set PROPMAKER_PWR high to power NeoPixels/Audio/RGB on the Prop-Maker
enable = digitalio.DigitalInOut(PROPMAKER_PWR)
enable.direction = digitalio.Direction.OUTPUT
enable.value = True

# Initialize the LED strips
leds = neopixel.NeoPixel(
    LED_PIN, NUM_LEDS, brightness=MAX_BRIGHTNESS, pixel_order=neopixel.GRBW)
leds.fill(IDLE_FADE)

# -----------------------------------------------------------------------------
# Event loop
# -----------------------------------------------------------------------------

# Loop blast forever (TODO: finish all the things)
while True:
    draw_blast(leds, BLAST_SPRITE)
