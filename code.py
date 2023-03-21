import time

from blaster import LOOP_SLEEP, LOGGER
from blaster.hardware import BlasterProp
from blaster.behavior import PropStateMachine, STATE_IDLE, IdleState, \
    ChargingState, ChargedState, FiringState

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
