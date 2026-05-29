#!/usr/bin/env python3
"""
waypoint_marker_publisher.py
────────────────────────────
Publishes RViz MarkerArray on /waypoint_markers so you can see
colored discs + floating text labels in RViz alongside Gazebo.

ROS 2 (Humble/Iron)

"""

import math
import sys

import rclpy
from rclpy.node import Node 
from visualization_msgs.msg import Marker, MarkerArray



# ── Waypoint definitions (keep in sync with waypoints.yaml) ──────────────
WAYPOINTS = [
    {"id": 0, "name": "WP0\nOrigin",   "x":  0.0, "y":  0.0, "r": 0.5, "g": 0.0, "b": 0.8},
    {"id": 1, "name": "WP1\nNW",       "x": -3.0, "y":  3.0, "r": 0.0, "g": 0.4, "b": 0.9},
    {"id": 2, "name": "WP2\nNE",       "x":  3.0, "y":  3.0, "r": 0.0, "g": 0.4, "b": 0.9},
    {"id": 3, "name": "WP3\nSW",       "x": -3.0, "y": -3.0, "r": 0.0, "g": 0.4, "b": 0.9},
    {"id": 4, "name": "WP4\nSE",       "x":  3.0, "y": -3.0, "r": 0.0, "g": 0.4, "b": 0.9},
    {"id": 5, "name": "WP5\nN-Mid",    "x":  0.0, "y":  3.0, "r": 1.0, "g": 0.5, "b": 0.0},
]

DISC_RADIUS    = 0.30   # metres
DISC_THICKNESS = 0.005  # metres
TEXT_HEIGHT    = 0.60   # metres above ground
TEXT_SCALE     = 0.25   # text size


def make_disc_marker(wp, frame_id="odom"):
    m = Marker()
    m.header.frame_id = frame_id
    m.ns    = "test_discs"
    m.id    = wp["id"]
    m.type  = Marker.CYLINDER
    m.action = Marker.ADD
    m.pose.position.x = wp["x"]
    m.pose.position.y = wp["y"]
    m.pose.position.z = DISC_THICKNESS / 2.0
    m.pose.orientation.w = 1.0
    m.scale.x = DISC_RADIUS * 2
    m.scale.y = DISC_RADIUS * 2
    m.scale.z = DISC_THICKNESS
    m.color.r = wp["r"]
    m.color.g = wp["g"]
    m.color.b = wp["b"]
    m.color.a = 1.0
    return m


def make_text_marker(wp, frame_id="odom"):
    m = Marker()
    m.header.frame_id = frame_id
    m.ns    = "test_labels"
    m.id    = wp["id"] + 100
    m.type  = Marker.TEXT_VIEW_FACING
    m.action = Marker.ADD
    m.pose.position.x = wp["x"]
    m.pose.position.y = wp["y"]
    m.pose.position.z = TEXT_HEIGHT
    m.pose.orientation.w = 1.0
    m.scale.z = TEXT_SCALE
    m.color.r = 1.0
    m.color.g = 1.0
    m.color.b = 1.0
    m.color.a = 1.0
    m.text = wp["name"]
    return m


def make_ring_marker(wp, frame_id="odom"):
    """A larger white ring around the disc for extra visibility."""
    m = Marker()
    m.header.frame_id = frame_id
    m.ns    = "test_rings"
    m.id    = wp["id"] + 200
    m.type  = Marker.CYLINDER
    m.action = Marker.ADD
    m.pose.position.x = wp["x"]
    m.pose.position.y = wp["y"]
    m.pose.position.z = 0.0015
    m.pose.orientation.w = 1.0
    m.scale.x = (DISC_RADIUS + 0.12) * 2
    m.scale.y = (DISC_RADIUS + 0.12) * 2
    m.scale.z = 0.001
    m.color.r = 1.0
    m.color.g = 1.0
    m.color.b = 1.0
    m.color.a = 0.9
    return m


# ── ROS 2 ────────────────────────────────────────────────────────────────
class WaypointMarkerNode(Node):
    def __init__(self):
        super().__init__("waypoint_marker_publisher")
        self.pub = self.create_publisher(MarkerArray, "/test_markers", 10)
        self.timer = self.create_timer(1.0, self.publish_markers)

    def publish_markers(self):
        ma = MarkerArray()
        #now = self.get_clock().now().to_msg()
        for wp in WAYPOINTS:
            ring = make_ring_marker(wp)
            #ring.header.stamp = now
            disc = make_disc_marker(wp)
            #disc.header.stamp = now
            text = make_text_marker(wp)
            #text.header.stamp = now
            ma.markers.append(ring)
            ma.markers.append(disc)
            ma.markers.append(text)
        self.pub.publish(ma)


def main(args=None):
    rclpy.init(args=args)
    node = WaypointMarkerNode()
    rclpy.spin(node)
    rclpy.shutdown()


# ── Entry point ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
