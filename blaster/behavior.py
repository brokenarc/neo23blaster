# SPDX-License-Identifier: MIT

"""Contains the program code for handling the blaster's behavior. This
includes the various prop states as well as the state machine to handle going
from one state to another.

Note that states' `update` methods do not have logging since they are called
many times per second.

The behavior of the prop is defined as:

1. Starts up in the IDLE state
2. Pressing the trigger causes a transition to the TRIGGER state
3. If the trigger is quickly released:
    a. Transition to FIRING state
    b. Return to IDLE state and wait for a trigger press
4. Else if the trigger stays down, transition to the CHARGING state
5. Once charged, transition to the CHARGED state
6. When the trigger is released, transition to FIRING state
7. Return to IDLE state and wait for a trigger press
"""

import time
from . import CHARGE_THRESHOLD, LOGGER
from .hardware import BlasterProp

# -----------------------------------------------------------------------------
# The names of the prop states.
STATE_CHARGED = 'CHARGED'
STATE_CHARGING = 'CHARGING'
STATE_FIRING = 'FIRING'
STATE_IDLE = 'IDLE'
STATE_TRIGGER = 'TRIGGER'


class PropState:
    """Defines the behavior of prop states.

    Parameters
    ----------
    name: str
        The name of this instance of the state.
    prop: BlasterProp
        The prop this state instance is bound to.
    """

    def __init__(self, name: str, prop: BlasterProp):
        self._name = name
        self._prop = prop

    @property
    def name(self) -> str:
        """str: The state name."""
        return self._name

    def enter(self):
        """Called when the state machine transitions to this state.
        """
        LOGGER.debug(f'--> {self.name}')

    def exit(self):
        """Called when the state machine prepares to transition to another
        state.
        """
        LOGGER.debug(f'<-- {self.name}')

    def update(self) -> str | None:
        """Called to provide the state an opportunity to perform updates and/or
        indicate that the state machine should transition to another state.

        Returns
        -------
        str or None
            The name of the next state to transition to or `None` if the state
            machine should remain in this state.
        """
        return None


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
            self.__states[state.name] = state

        if initial_state:
            self.state = initial_state

    @property
    def state(self) -> str:
        """str: The name of the state machine's current state.

        When the property's value is changed, the current state's `exit` method
        is invoked before the new state's `enter` method is invoked.
        """
        return self._state.name

    @state.setter
    def state(self, value: str):
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
# The prop states.
# -----------------------------------------------------------------------------


class IdleState(PropState):
    """Models the idle state.

    Parameters
    ----------
    prop : BlasterProp
        The prop this state instance is bound to.
    """

    def __init__(self, prop: BlasterProp):
        super().__init__(STATE_IDLE, prop)

    def enter(self):
        """Fill the NeoPixel strip with the idle color.
        """
        super().enter()
        self._prop.play_idle_effect()

    def update(self) -> str | None:
        """Check to see if the trigger switch has been pressed.

        Returns
        -------
        str or None
            `STATE_TRIGGER` if the trigger has been pressed, otherwise `None`.
        """
        return STATE_TRIGGER if self._prop.trigger else None


class TriggerState(PropState):
    """Models the trigger state behavior that measures how long the trigger is
    held down to determine the next state.

    Parameters
    ----------
    prop : BlasterProp
        The prop this state instance is bound to.
    """

    def __init__(self, prop: BlasterProp):
        super().__init__(STATE_TRIGGER, prop)
        self.__time = 0

    def enter(self):
        """Start the trigger press timer.
        """
        super().enter()
        self.__time = time.monotonic()

    def update(self) -> str | None:
        """Check to see if the trigger was released quickly enough for the
        firing state or if it has been held down long enough to start charging.

        Returns
        -------
        str or None
            - `STATE_FIRING` if the trigger was released quickly
            - `STATE_CHARGING` if the trigger was held down longer than the
              charge threshold.
            - `None` if neither condition is met
        """
        delta = abs(time.monotonic() - self.__time)
        if self._prop.trigger:
            return STATE_CHARGING if delta > CHARGE_THRESHOLD else None
        else:
            return STATE_FIRING


class ChargedState(PropState):
    """Models the charged state.

    Parameters
    ----------
    prop : BlasterProp
        The prop this state instance is bound to.
    """

    def __init__(self, prop: BlasterProp):
        super().__init__(STATE_CHARGED, prop)

    def update(self) -> str | None:
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

    def __init__(self, prop: BlasterProp):
        super().__init__(STATE_CHARGING, prop)

    def enter(self):
        """Animate the charging effect on the prop's NeoPixel strip.
        """
        super().enter()
        self._prop.play_charging_effect()

    def update(self) -> str | None:
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

    def __init__(self, prop: BlasterProp):
        super().__init__(STATE_FIRING, prop)

    def enter(self):
        """Animate the firing effect on the prop's NeoPixel strip.
        """
        super().enter()
        self._prop.play_firing_effect()

    def update(self) -> str | None:
        """Transition to the idle state.

        Returns
        -------
        str
            Always returns `STATE_IDLE`.
        """
        return STATE_IDLE
