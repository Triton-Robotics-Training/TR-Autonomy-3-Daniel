"""Compare each camera detection with the nearest ground-truth panel."""

from collections import deque

import rclpy
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.time import Time
from std_msgs.msg import Float64
from tf2_ros import Buffer, TransformException, TransformListener
from tr_messages.msg import DetWithImg


class ErrorCalculator(Node):
    def __init__(self):
        super().__init__('calc_error')
        self.tf_buffer = Buffer(node=self)
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.pending = deque(maxlen=100)
        self.last_detection_stamp = None
        self.last_published_stamp = None
        self.publishers_by_axis = [
            self.create_publisher(Float64, f'{axis}_err', 10)
            for axis in ('x', 'y', 'z')
        ]
        self.create_subscription(DetWithImg, '/detections', self.on_detection, 10)
        self.create_timer(0.05, self.process_detections)

    def on_detection(self, msg):
        if not any(detection.results for detection in msg.detection_info.detections):
            return
        stamp = Time.from_msg(msg.detection_info.header.stamp)
        if stamp.nanoseconds == 0 or (
            self.last_detection_stamp is not None
            and stamp == self.last_detection_stamp
        ):
            return
        if self.last_detection_stamp is not None and stamp < self.last_detection_stamp:
            self.pending.clear()
            self.last_published_stamp = None
        self.last_detection_stamp = stamp
        self.pending.append(stamp)

    def process_detections(self):
        for _ in range(len(self.pending)):
            stamp = self.pending.popleft()
            if self.last_published_stamp is not None and stamp <= self.last_published_stamp:
                continue
            age = self.get_clock().now() - stamp
            if age < Duration(seconds=0.1):
                self.pending.append(stamp)
                continue
            if age > Duration(seconds=3.0):
                continue
            try:
                detected = self.tf_buffer.lookup_transform(
                    'map', 'detected_panel', stamp
                ).transform.translation
                panels = [
                    self.tf_buffer.lookup_transform(
                        'map', f'panel_{index}', stamp
                    ).transform.translation
                    for index in range(4)
                ]
            except TransformException:
                self.pending.append(stamp)
                continue

            nearest = min(
                panels,
                key=lambda panel: (
                    (detected.x - panel.x) ** 2
                    + (detected.y - panel.y) ** 2
                    + (detected.z - panel.z) ** 2
                ),
            )
            # Each error is the estimated position minus the ground truth.
            for publisher, error in zip(
                self.publishers_by_axis,
                (detected.x - nearest.x, detected.y - nearest.y, detected.z - nearest.z),
            ):
                publisher.publish(Float64(data=error))
            self.last_published_stamp = stamp


def main():
    rclpy.init()
    node = ErrorCalculator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
