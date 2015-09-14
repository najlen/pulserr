# pulserr

Use phidget-sersors to measure you electricity consumption in real time. Phidget sensor should be mounted on the LED on electricity meter.

* eventToRabbit.py

Listen for events from phidgets sensors and push to a rabbitmq. This raw sensor data can then be consumed from the rabbitmq queue.

* eventsToPulse.py

Consume raw sensor events and identify pulses. Push pulses to rabbitmq.

* pulseToDB.py

Consume pulses and submit to db. Creates a local sqlite db with a counter per day.

* pulseToCurrentConsumption.py

Consume pulses and calculate the current delta. The time between pulses tells the current electricity consumption. This module can also push values to a gecko board Geck-o-Meter (https://support.geckoboard.com/hc/en-us/articles/203674058-Geck-o-Meter).

