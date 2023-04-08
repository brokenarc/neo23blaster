# SPDX-License-Identifier: MIT

import time

from blaster import BATTERY_TIME, BEHAVIOR_TIME, LOGGER
from blaster.hardware import BlasterProp
from blaster.behavior import STATE_IDLE, ChargingState, ChargedState, \
    FiringState, IdleState, PropStateMachine, TriggerState

# -----------------------------------------------------------------------------
# Initialize the prop and state machine
# -----------------------------------------------------------------------------
prop = BlasterProp()
state_machine = PropStateMachine(
    states=[
        IdleState(prop),
        TriggerState(prop),
        ChargingState(prop),
        ChargedState(prop),
        FiringState(prop)
    ],
    initial_state=STATE_IDLE)

# -----------------------------------------------------------------------------
# Event loop
# -----------------------------------------------------------------------------
LOGGER.info('Starting event loop')
behavior_time = 0
battery_time = 0

while True:
    now = time.monotonic()

    if (now - behavior_time) >= BEHAVIOR_TIME:
        state_machine.update()
        behavior_time = now

    if (now - battery_time) >= BATTERY_TIME:
        prop.update_battery()
        battery_time = now
