# pulserr

Use phidget-sersors to measure you electricity consumption in real time.

* eventToRabbit.py

Listen for events from phidgets sensors and push to a rabbitmq. This raw sensor data can then be consumed from the rabbitmq queue.

* eventsToPulse.py

Consume raw sensor events and identify pulses. Push pulses to rabbitmq.

* pulseToDB.py

Consume pulses and submit to db. Creates a local sqlite db.

* pulseToCurrentConsumption.py

Consume pulses and calculate the current delta.

## Todo
* pulseToGecko.py

Consume pulses and submit to Geckoboard.