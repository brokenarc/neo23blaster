import os
import time
import digitalio
import board
import neopixel
import adafruit_logging as logging

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
# Attempt to get the logging level from settings.toml, falling back to the
# WARNING level.
LOG_LEVEL = os.getenv('LOG_LEVEL', logging.WARNING)
LOGGER = logging.getLogger('prop')
LOGGER.setLevel(LOG_LEVEL)

# How long to sleep between update checks in the event loop
LOOP_SLEEP = 0.1

# -----------------------------------------------------------------------------
# Color scheme
# -----------------------------------------------------------------------------
IDLE_FULL = (0, 68, 255, 0)  # Bright ice blue
IDLE_FADE = (0, 11, 42, 0)  # Dark blue
CHARGE_FADE = (0, 22, 64, 0)  # Medium blue
BLAST_FULL = (255, 0, 0, 0)  # Bright red
BLAST_FADE = (25, 0, 0, 0)  # Dark red


class BlasterProp:
    """Contains the settings and program logic specific to the hardware
    components.
    """
    PROPMAKER_PWR = board.D10
    PROPMAKER_SWITCH = board.D9
    LED_PIN = board.D5
    NUM_LEDS = 15
    MAX_BRIGHTNESS = 1 / 3
    PIXEL_ORDER = neopixel.GRBW

    def __init__(self):
        # Set PROPMAKER_PWR high to power NeoPixels/Audio/RGB on the Prop-Maker
        self.propmaker_power = digitalio.DigitalInOut(
            BlasterProp.PROPMAKER_PWR)
        self.propmaker_power.direction = digitalio.Direction.OUTPUT
        self.propmaker_power.value = True

        # Set up the switch
        self.switch = digitalio.DigitalInOut(BlasterProp.PROPMAKER_SWITCH)
        self.switch.switch_to_input(pull=digitalio.Pull.UP)

        # Initialize the LED strips
        self.leds = neopixel.NeoPixel(BlasterProp.LED_PIN, BlasterProp.NUM_LEDS,
                                      brightness=BlasterProp.MAX_BRIGHTNESS,
                                      pixel_order=BlasterProp.PIXEL_ORDER)
        LOGGER.info('Hardware initialization complete')

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


# -----------------------------------------------------------------------------
# Prop states and state machine
# 
# Note that states' `update` methods do not have logging since they are called
# many times per second.
# -----------------------------------------------------------------------------
# The names of the prop states.
STATE_IDLE = 'IDLE'
STATE_CHARGED = 'CHARGED'
STATE_CHARGING = 'CHARGING'
STATE_FIRING = 'FIRING'


class PropState:
    """Defines the behavior of prop states.

    Parameters
    ----------
    name: str
        The name of this instance of the state.
    prop: BlasterProp
        The prop this state instance is bound to.
    """

    def __init__(self, name, prop):
        self._name = name
        self._prop = prop

    @property
    def name(self):
        """str: The state name."""
        return self._name

    def enter(self):
        """Called when the state machine transitions to this state.
        """
        LOGGER.debug(f'Entering state {self.name}')

    def exit(self):
        """Called when the state machine prepares to transition to another
        state.
        """
        LOGGER.debug(f'Exiting state {self.name}')

    def update(self):
        """Called to provide the state an opportunity to perform updates and/or
        indicate that the state machine should transition to another state.

        Returns
        -------
        str or None
            The name of the next state to transition to or `None` if the state
            machine should remain in this state.
        """
        return None


class IdleState(PropState):
    """Models the idle state.

    Parameters
    ----------
    prop : BlasterProp
        The prop this state instance is bound to.
    """

    def __init__(self, prop):
        super().__init__(STATE_IDLE, prop)

    def enter(self):
        """Fill the NeoPixel strip with the idle color.
        """
        super().enter()
        self._prop.leds.fill(IDLE_FADE)

    def exit(self):
        super().exit()

    def update(self):
        """Check to see if the trigger switch has been pressed.

        Returns
        -------
        str or None
            `STATE_CHARGING` if the switch has been pressed, otherwise `None`.
        """
        switch = self._prop.switch.value
        return STATE_CHARGING if not switch else None


class ChargedState(PropState):
    """Models the charged state.

    Parameters
    ----------
    prop : BlasterProp
        The prop this state instance is bound to.
    """

    def __init__(self, prop):
        super().__init__(STATE_CHARGED, prop)

    def enter(self):
        """Fill the NeoPixel strip with the idle color.
        """
        super().enter()

    def exit(self):
        super().exit()

    def update(self):
        """Check to see if the trigger switch has been released.

        Returns
        -------
        str or None
            `STATE_FIRING` if the switch has been released, otherwise `None`.
        """
        switch = self._prop.switch.value
        return STATE_FIRING if switch else None


class ChargingState(PropState):
    """Models the charging state.

    Parameters
    ----------
    prop : BlasterProp
        The prop this state instance is bound to.
    """

    # The sprite to use for the charging effect.
    CHARGE_SPRITE = (CHARGE_FADE, IDLE_FULL, IDLE_FULL, CHARGE_FADE)

    def __init__(self, prop):
        super().__init__(STATE_CHARGING, prop)

    def enter(self):
        """Animate the charging effect on the prop's NeoPixel strip.
        """
        super().enter()
        self._prop.animate_sprite(ChargingState.CHARGE_SPRITE)

    def exit(self):
        super().exit()

    def update(self):
        """Transition to the charged state.

        Returns
        -------
        str
            Always returns `STATE_CHARGED`.
        """
        return STATE_CHARGED


class FiringState(PropState):
    """Models the firing state.

    Parameters
    ----------
    prop : BlasterProp
        The prop this state instance is bound to.
    """

    # The sprite to use for the firing effect.
    BLAST_SPRITE = (IDLE_FADE, BLAST_FADE, BLAST_FULL, BLAST_FADE, IDLE_FADE)

    def __init__(self, prop):
        super().__init__(STATE_FIRING, prop)

    def enter(self):
        """Animate the firing effect on the prop's NeoPixel strip.
        """
        super().enter()
        self._prop.animate_sprite(FiringState.BLAST_SPRITE)

    def exit(self):
        super().exit()

    def update(self):
        """Transition to the idle state.

        Returns
        -------
        str
            Always returns `STATE_IDLE`.
        """
        return STATE_IDLE


class PropStateMachine:
    """Provides a simple state machine to manage the prop's behavior.

    The state machine spends most of its time waiting for its `update` method
    to be called. It then delegates control to the current state and responds
    accordingly.

    When the machine is created:
        1. Set current state to initial state.
        2. Call `enter` on current state.

    When the machine's `update` method is called:
        1. Call `update` on current state.
        2. Did that return the name of the next state?
            a. Yes?
                1. Call `exit` on the current state
                2. Set the current state to be the returned state
                3. Call `enter` on the new current state
            b. No?
                1. Return and wait to be called again.

    When the machine's state is manually set:
        1. Call `exit` on the current state.
        2. Set the current state to what was specified.
        3. Call `enter` on the new manually set state.

    Parameters
    ----------
    states : array-like(PropState)
        All of the possible states for this state machine, indexed by name.
    initial_state : str, optional
        If given, the state machine will transition to this state immediately.
    """

    def __init__(self, states, initial_state=None):
        self.__state = None
        self.__states = {}

        for state in states:
            LOGGER.debug(f'Adding: {state.name}')
            self.__states[state.name] = state

        if initial_state:
            self.state = initial_state

    @property
    def state(self):
        """str: The name of the state machine's current state.

        When the property's value is changed, the current state's `exit` method
        is invoked before the new state's `enter` method is invoked.
        """
        return self._state.name

    @state.setter
    def state(self, value):
        LOGGER.debug(f'Going to state: {value}')
        if self.__state:
            self.__state.exit()

        self.__state = self.__states[value]
        self.__state.enter()

    def update(self):
        """Invokes the current state's `update` method and transitions to the
        next state if the name of a state was returned.
        """
        if self.__state:
            next_state = self.__state.update()

            if next_state:
                self.state = next_state


# -----------------------------------------------------------------------------
# Initialize the prop and state machine
# -----------------------------------------------------------------------------
prop = BlasterProp()
state_machine = PropStateMachine(
    states=[
        IdleState(prop),
        ChargingState(prop),
        ChargedState(prop),
        FiringState(prop)
    ],
    initial_state=STATE_IDLE)

# -----------------------------------------------------------------------------
# Event loop
# -----------------------------------------------------------------------------
LOGGER.info('Starting event loop')
while True:
    state_machine.update()
    time.sleep(LOOP_SLEEP)
