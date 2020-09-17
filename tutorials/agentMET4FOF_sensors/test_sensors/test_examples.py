from agentMET4FOF_sensors.buffer_sensor import main as buffer_sensor_main


def test_buffer_sensor():
    buffer_sensor_main().shutdown()
