"""
Math utilities for game calculations.
"""

import math
import random


def distance(x1, y1, x2, y2):
    """Calculate distance between two points."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def distance_squared(x1, y1, x2, y2):
    """Calculate squared distance between two points (faster)."""
    return (x2 - x1) ** 2 + (y2 - y1) ** 2


def angle_to_target(x1, y1, x2, y2):
    """Calculate angle from point 1 to point 2."""
    return math.atan2(y2 - y1, x2 - x1)


def move_towards(x, y, target_x, target_y, speed):
    """Move a point towards a target at given speed."""
    dx = target_x - x
    dy = target_y - y
    dist = math.sqrt(dx * dx + dy * dy)
    
    if dist <= speed:
        return target_x, target_y
    
    # Normalize and scale by speed
    dx = (dx / dist) * speed
    dy = (dy / dist) * speed
    
    return x + dx, y + dy


def clamp(value, min_val, max_val):
    """Clamp a value between min and max."""
    return max(min_val, min(max_val, value))


def lerp(a, b, t):
    """Linear interpolation between a and b by factor t."""
    return a + (b - a) * t


def random_point_in_circle(center_x, center_y, radius):
    """Generate a random point within a circle."""
    angle = random.uniform(0, 2 * math.pi)
    r = random.uniform(0, radius)
    x = center_x + r * math.cos(angle)
    y = center_y + r * math.sin(angle)
    return x, y


def normalize_angle(angle):
    """Normalize angle to be between -π and π."""
    while angle > math.pi:
        angle -= 2 * math.pi
    while angle < -math.pi:
        angle += 2 * math.pi
    return angle 