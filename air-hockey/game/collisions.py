"""
Robust puck-vs-paddle collision handling.
"""


def handle_paddle_collision(puck, paddle):
    """
    Resolve a circular puck/paddle collision.

    The puck is pushed back outside the paddle and its velocity is reflected
    across the collision normal. The bounce is only applied when the puck
    is moving toward the paddle, preventing repeated flips while overlapping.
    Returns True when an overlap was resolved.
    """
    dx = puck.x - paddle.x
    dy = puck.y - paddle.y
    min_distance = puck.radius + paddle.radius
    distance_sq = dx * dx + dy * dy

    if distance_sq >= min_distance * min_distance:
        return False

    if distance_sq == 0:
        # Fallback if both centers are exactly coincident.
        nx, ny = 1.0, 0.0
        distance = 0.0
    else:
        distance = distance_sq ** 0.5
        nx, ny = dx / distance, dy / distance

    # Push the puck completely outside the paddle.
    overlap = min_distance - distance
    puck.x += nx * overlap
    puck.y += ny * overlap

    # Reflect only if the puck is travelling into the paddle.
    velocity_toward_paddle = puck.vx * nx + puck.vy * ny

    if velocity_toward_paddle < 0:
        puck.vx -= 2 * velocity_toward_paddle * nx
        puck.vy -= 2 * velocity_toward_paddle * ny

    return True