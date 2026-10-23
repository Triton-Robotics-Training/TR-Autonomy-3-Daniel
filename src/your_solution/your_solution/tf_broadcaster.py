"""Broadcast detected and ground-truth panel poses as ROS transforms."""

import rclpy
from geometry_msgs.msg import TransformStamped
from rclpy.node import Node
from tf2_ros import TransformBroadcaster
from tr_messages.msg import DetWithImg, SimGroundTruth


class PanelTfBroadcaster(Node):
    def __init__(self):
        super().__init__('tf_broadcaster')
        self.broadcaster = TransformBroadcaster(self)
        self.create_subscription(
            SimGroundTruth,
            '/simulation/ground_truth',
            self.on_ground_truth,
            10,
        )
        self.create_subscription(
            DetWithImg,
            '/detections',
            self.on_detection,
            10,
        )

    def send_pose(self, parent, child, pose, stamp):
        transform = TransformStamped()
        transform.header.stamp = stamp
        transform.header.frame_id = parent
        transform.child_frame_id = child
        transform.transform.translation.x = pose.position.x
        transform.transform.translation.y = pose.position.y
        transform.transform.translation.z = pose.position.z
        transform.transform.rotation = pose.orientation
        self.broadcaster.sendTransform(transform)

    def on_ground_truth(self, msg):
        self.send_pose(
            'map', 'camera_frame', msg.primary_robot.camera_pose, msg.header.stamp
        )
        for index, pose in enumerate(msg.secondary_robot.armor_panel_poses):
            self.send_pose('map', f'panel_{index}', pose, msg.header.stamp)

    def on_detection(self, msg):
        for detection in msg.detection_info.detections:
            if detection.results:
                # SolvePnP reports this pose relative to the camera.
                self.send_pose(
                    'camera_frame',
                    'detected_panel',
                    detection.results[0].pose.pose,
                    msg.detection_info.header.stamp,
                )
                break


def main():
    rclpy.init()
    node = PanelTfBroadcaster()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
