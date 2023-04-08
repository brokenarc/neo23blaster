# Neo23Blaster

This project is the CircuitPython prototype for a blaster prop using NeoPixel LED strips.

## Parts

These components were used for the project:

* [Adafruit Feather M4 CAN Express](https://www.adafruit.com/product/4759) - A standard [Feather M4 Express](https://www.adafruit.com/product/3857) can also be used. This model was used because it was available when the project was being built.
* [Adafruit Prop-Maker FeatherWing](https://www.adafruit.com/product/3988)
* [Adafruit Mini Skinny NeoPixel RGBW LED Strip](https://www.adafruit.com/product/4914)

## Installation

You must install the following dependencies from the [Adafruit CircuitPython library bundle](https://circuitpython.org/libraries) that matches the version of CircuitPython on your M4. Copy this file to the `lib` directory on the `CIRCUITPY` drive.

* `adafruit_logging.mpy`

Finally, copy the `code.py` file, `settings.toml` file, the `sounds` directory, and the `blaster` directory to the `CIRCUITPY` drive that mounts when the Feather board is connected via USB.

If you wish to adjust the logging level for debugging, edit the setting named `LOG_LEVEL` in your `settings.toml` file with the desired [numeric level](https://learn.adafruit.com/a-logger-for-circuitpython/using-a-logger).
