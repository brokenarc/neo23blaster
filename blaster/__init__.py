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

# -----------------------------------------------------------------------------
# Color scheme
# -----------------------------------------------------------------------------
IDLE_FULL = (0, 68, 255, 0)  # Bright ice blue
IDLE_FADE = (0, 11, 42, 0)  # Dark blue
CHARGE_FADE = (0, 22, 64, 0)  # Medium blue
BLAST_FULL = (255, 0, 0, 0)  # Bright red
BLAST_FADE = (25, 0, 0, 0)  # Dark red
