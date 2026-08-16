from dataclasses import dataclass
from itertools import count
import heapq

@dataclass(frozen=True)
class Point:
    x: float
    y: float
    data: object = None

class Rectangle:
    def __init__(self, x, y, width, height):
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)

    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x + self.width

    @property
    def bottom(self):
        return self.y

    @property
    def top(self):
        return self.y + self.height

    def contains(self, point):
        return (
            self.left <= point.x <= self.right
            and self.bottom <= point.y <= self.top
        )

    def distance_squared_to_point(self, point):
        if point.x < self.left:
            dx = self.left - point.x
        elif point.x > self.right:
            dx = point.x - self.right
        else:
            dx = 0.0

        if point.y < self.bottom:
            dy = self.bottom - point.y
        elif point.y > self.top:
            dy = point.y - self.top
        else:
            dy = 0.0

        return dx * dx + dy * dy


class Quadtree:
    def __init__(self, boundary, capacity=4):
        self.boundary = boundary
        self.capacity = capacity
        self.points = []
        self.divided = False
        self.children = []

    def subdivide(self):
        if self.divided:
            return

        half_w = self.boundary.width / 2.0
        half_h = self.boundary.height / 2.0
        x = self.boundary.x
        y = self.boundary.y

        self.children = [
            Quadtree(Rectangle(x, y, half_w, half_h), self.capacity),
            Quadtree(Rectangle(x + half_w, y, half_w, half_h), self.capacity),
            Quadtree(Rectangle(x, y + half_h, half_w, half_h), self.capacity),
            Quadtree(Rectangle(x + half_w, y + half_h, half_w, half_h), self.capacity),
        ]
        self.divided = True

        old_points = self.points
        self.points = []
        for point in old_points:
            inserted = self._insert_into_child(point)
            if not inserted:
                self.points.append(point)

    def _insert_into_child(self, point):
        for child in self.children:
            if child.boundary.contains(point) and child.insert(point):
                return True
        return False

    def insert(self, point):
        if not self.boundary.contains(point):
            return False

        if not self.divided and len(self.points) < self.capacity:
            self.points.append(point)
            return True

        if not self.divided:
            self.subdivide()

        if self._insert_into_child(point):
            return True

        self.points.append(point)
        return True

    def remove(self, point):
        if not self.boundary.contains(point):
            return False

        for index, stored_point in enumerate(self.points):
            if stored_point is point:
                del self.points[index]
                return True

        if self.divided:
            for child in self.children:
                if child.boundary.contains(point) and child.remove(point):
                    return True

        return False

    def find_k_nearest(self, query_point, k=5):
        if k <= 0:
            raise ValueError("k must be greater than 0.")

        candidate_heap = []
        tie_breaker = count()

        def consider(point):
            distance_sq = (point.x - query_point.x) ** 2 + (point.y - query_point.y) ** 2
            item = (-distance_sq, next(tie_breaker), point)
            if len(candidate_heap) < k:
                heapq.heappush(candidate_heap, item)
            elif distance_sq < -candidate_heap[0][0]:
                heapq.heapreplace(candidate_heap, item)

        def visit(node):
            if len(candidate_heap) == k:
                farthest_sq = -candidate_heap[0][0]
                if node.boundary.distance_squared_to_point(query_point) > farthest_sq:
                    return

            for point in node.points:
                consider(point)

            if node.divided:
                children = sorted(
                    node.children,
                    key=lambda child: child.boundary.distance_squared_to_point(query_point)
                )
                for child in children:
                    visit(child)

        visit(self)

        result = [
            (-negative_distance, sequence, point)
            for negative_distance, sequence, point in candidate_heap
        ]
        result.sort(key=lambda item: (item[0], getattr(item[2].data, "id", ""), item[1]))
        return [item[2] for item in result]

    def all_points(self):
        result = list(self.points)
        if self.divided:
            for child in self.children:
                result.extend(child.all_points())
        return result
