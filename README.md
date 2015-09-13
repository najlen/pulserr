# pulserr

Use phidget-sersors to measure you electricity consumption in real time.

* eventToRabbit.py

Listen for events from phidgets sensors and push to a rabbitmq. This raw sensor data can then be consumed from the rabbitmq queue.

* eventsToPulse.py

Consume raw sensor events and identify pulses. Push pulses to rabbitmq.

## Todo
* pulseToDB.py

Consume pulses and submit to db.

* pulseToGecko.py

Consume pulses and submit to Geckoboard.