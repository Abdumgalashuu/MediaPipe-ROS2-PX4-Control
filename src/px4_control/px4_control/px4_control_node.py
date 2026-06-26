import asyncio
import threading

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from mavsdk import System
from mavsdk.offboard import OffboardError, VelocityNedYaw


SPEED = 0.5
TAKEOFF_ALTITUDE = 3.0


class PX4ControlNode(Node):
    def __init__(self):
        super().__init__("px4_control_node")

        self.command = "STOP"
        self.drone = System()
        self.loop = asyncio.new_event_loop()

        self.subscriber = self.create_subscription(
            String,
            "/gesture_cmd",
            self.gesture_callback,
            10
        )

        self.get_logger().info("PX4 control node başladı")
        self.async_thread = threading.Thread(target=self.start_async_loop, daemon=True)
        self.async_thread.start()

    def gesture_callback(self, msg):
        self.command = msg.data
        self.get_logger().info(f"Gesture geldi: {self.command}")

    def start_async_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.drone_main())

    def command_to_velocity(self, command):
        if command == "FORWARD":
            return VelocityNedYaw(SPEED, 0.0, 0.0, 0.0)
        elif command == "BACKWARD":
            return VelocityNedYaw(-SPEED, 0.0, 0.0, 0.0)
        elif command == "RIGHT":
            return VelocityNedYaw(0.0, SPEED, 0.0, 0.0)
        elif command == "LEFT":
            return VelocityNedYaw(0.0, -SPEED, 0.0, 0.0)
        else:
            return VelocityNedYaw(0.0, 0.0, 0.0, 0.0)

    async def drone_main(self):
        self.get_logger().info("PX4'e bağlanılıyor...")
        await self.drone.connect(system_address="udp://:14540")

        async for state in self.drone.core.connection_state():
            if state.is_connected:
                self.get_logger().info("PX4 bağlantısı tamam")
                break

        await self.drone.action.set_takeoff_altitude(TAKEOFF_ALTITUDE)

        self.get_logger().info("Arm ediliyor...")
        await self.drone.action.arm()

        self.get_logger().info("3 metre kalkış...")
        await self.drone.action.takeoff()

        await asyncio.sleep(8)

        self.get_logger().info("Offboard hazırlanıyor...")
        await self.drone.offboard.set_velocity_ned(
            VelocityNedYaw(0.0, 0.0, 0.0, 0.0)
        )

        try:
            await self.drone.offboard.start()
            self.get_logger().info("Offboard başladı")
        except OffboardError as error:
            self.get_logger().error(f"Offboard başlatılamadı: {error}")
            await self.drone.action.land()
            return

        while rclpy.ok():
            velocity = self.command_to_velocity(self.command)
            await self.drone.offboard.set_velocity_ned(velocity)
            await asyncio.sleep(0.1)

        self.get_logger().info("ROS kapanıyor, iniş yapılıyor...")
        await self.drone.offboard.set_velocity_ned(
            VelocityNedYaw(0.0, 0.0, 0.0, 0.0)
        )
        await asyncio.sleep(1)
        await self.drone.action.land()


def main(args=None):
    rclpy.init(args=args)
    node = PX4ControlNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
