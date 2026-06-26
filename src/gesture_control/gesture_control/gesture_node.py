import cv2
import mediapipe as mp
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class GestureNode(Node):
    def __init__(self):
        super().__init__("gesture_node")
        self.publisher = self.create_publisher(String, "/gesture_cmd", 10)

        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.45,
            min_tracking_confidence=0.45
        )

        self.timer = self.create_timer(0.03, self.loop)
        self.get_logger().info("MediaPipe gesture node başladı")

    def loop(self):
        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().warn("Kamera okunamadı")
            return

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        x1, x2 = w // 3, 2 * w // 3
        y1, y2 = h // 3, 2 * h // 3

        command = "STOP"

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb)

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), -1)
        cv2.line(frame, (x1, 0), (x1, h), (255, 255, 255), 2)
        cv2.line(frame, (x2, 0), (x2, h), (255, 255, 255), 2)
        cv2.line(frame, (0, y1), (w, y1), (255, 255, 255), 2)
        cv2.line(frame, (0, y2), (w, y2), (255, 255, 255), 2)

        if result.multi_hand_landmarks:
            hand = result.multi_hand_landmarks[0]
            tip = hand.landmark[8]

            ix = int(tip.x * w)
            iy = int(tip.y * h)

            cv2.circle(frame, (ix, iy), 12, (0, 255, 0), -1)
            self.mp_draw.draw_landmarks(frame, hand, self.mp_hands.HAND_CONNECTIONS)

            if x1 < ix < x2 and y1 < iy < y2:
                command = "STOP"
            elif iy < y1:
                command = "FORWARD"
            elif iy > y2:
                command = "BACKWARD"
            elif ix < x1:
                command = "LEFT"
            elif ix > x2:
                command = "RIGHT"

        msg = String()
        msg.data = command
        self.publisher.publish(msg)

        cv2.putText(frame, f"COMMAND: {command}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

        cv2.imshow("ROS2 MediaPipe Gesture Node", frame)
        cv2.waitKey(1)

    def destroy_node(self):
        self.cap.release()
        cv2.destroyAllWindows()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = GestureNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
