#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, Range


class UltrasonicConverter(Node):

    def __init__(self):
        super().__init__('ultrasonic_converter')

        self.sensor_subscriptions = []
        self.sensor_publishers = {}

        sensors = [
            'front_left',
            'front_right',
            'rear_left',
            'rear_right',
            'left',
            'right'
        ]

        for sensor in sensors:
            input_topic = f'/ultrasonic/us_{sensor}/scan'
            output_topic = f'/ultrasonic/{sensor}'

            self.sensor_publishers[sensor] = self.create_publisher(
                Range, output_topic, 10
            )

            subscription = self.create_subscription(
                LaserScan,
                input_topic,
                lambda msg, name=sensor: self.convert_scan(msg, name),
                10
            )

            self.sensor_subscriptions.append(subscription)

            self.get_logger().info(
                f'{input_topic} -> {output_topic}'
            )

    def convert_scan(self, msg, sensor):

        valid = [
            value for value in msg.ranges
            if math.isfinite(value)
            and msg.range_min <= value <= msg.range_max
        ]

        if valid:
            distance = min(valid)
        elif any(math.isinf(value) and value < 0 for value in msg.ranges):
            distance = float('-inf')
        else:
            distance = float('inf')

        result = Range()

        result.header.stamp = msg.header.stamp
        result.header.frame_id = f'us_{sensor}_range_frame'

        result.radiation_type = Range.ULTRASOUND
        result.field_of_view = msg.angle_max - msg.angle_min
        result.min_range = msg.range_min
        result.max_range = msg.range_max
        result.range = distance

        self.sensor_publishers[sensor].publish(result)


def main(args=None):
    rclpy.init(args=args)
    node = UltrasonicConverter()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()