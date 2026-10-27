from collections import deque
from types import SimpleNamespace as NS
import unittest

from rclpy.clock import ClockType
from rclpy.time import Time
from tf2_ros import LookupException
from your_solution.calc_error.calc_error import ErrorCalculator


class Publisher:
    def __init__(self):
        self.values = []

    def publish(self, msg):
        self.values.append(msg.data)


def transform(x, y, z):
    return NS(transform=NS(translation=NS(x=x, y=y, z=z)))


def ros_time(seconds):
    return Time(seconds=seconds, clock_type=ClockType.ROS_TIME)


class Buffer:
    def __init__(self):
        self.calls = []

    def lookup_transform(self, parent, child, stamp):
        self.calls.append((parent, child, stamp.nanoseconds))
        if stamp.nanoseconds == 100_000_000_000:
            raise LookupException('early transform unavailable')
        positions = {
            'detected_panel': (1.5, 2.0, 3.0),
            'panel_0': (0.0, 0.0, 0.0),
            'panel_1': (1.0, 2.5, 2.75),
            'panel_2': (9.0, 9.0, 9.0),
            'panel_3': (7.0, 7.0, 7.0),
        }
        return transform(*positions[child])


class Tests(unittest.TestCase):
    def test_nearest_panel_timestamp_and_no_stale_output(self):
        node = NS(
            pending=deque([ros_time(100), ros_time(101)]),
            last_published_stamp=None,
            tf_buffer=Buffer(),
            publishers_by_axis=[Publisher(), Publisher(), Publisher()],
            get_clock=lambda: NS(now=lambda: ros_time(102)),
        )
        ErrorCalculator.process_detections(node)
        self.assertEqual([p.values for p in node.publishers_by_axis], [[0.5], [-0.5], [0.25]])
        successful_calls = [call for call in node.tf_buffer.calls if call[2] == 101_000_000_000]
        self.assertEqual(len(successful_calls), 5)
        self.assertEqual({call[0] for call in successful_calls}, {'map'})
        ErrorCalculator.process_detections(node)
        self.assertEqual([len(p.values) for p in node.publishers_by_axis], [1, 1, 1])

    def test_empty_detection_does_not_queue_or_publish(self):
        node = NS(pending=deque(), last_detection_stamp=None)
        message = NS(detection_info=NS(detections=[], header=NS(stamp=ros_time(100).to_msg())))
        ErrorCalculator.on_detection(node, message)
        self.assertEqual(len(node.pending), 0)

    def test_simulation_clock_reset_clears_old_detections(self):
        node = NS(
            pending=deque([ros_time(100)]),
            last_detection_stamp=ros_time(101),
            last_published_stamp=ros_time(100),
        )
        message = NS(detection_info=NS(
            detections=[NS(results=[object()])],
            header=NS(stamp=ros_time(1).to_msg()),
        ))
        ErrorCalculator.on_detection(node, message)
        self.assertEqual(list(node.pending), [ros_time(1)])
        self.assertIsNone(node.last_published_stamp)


if __name__ == '__main__':
    unittest.main()
