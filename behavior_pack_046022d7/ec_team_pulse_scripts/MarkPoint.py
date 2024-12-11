# -*- coding: utf-8 -*-

class MarkPoint(object):

    def __init__(self, point_id, pos, owner, mark_type, color, texture, remove_time):
        self.point_id = point_id  # type: int | None
        self.pos = pos  # type: tuple[float, float, float]
        self.owner = owner  # type: str
        self.mark_type = mark_type  # type: str
        self.color = color  # type: tuple[int, int, int]
        self.texture = texture  # type: str
        self.remove_time = remove_time  # type: float

    def to_dict(self):
        return {
            "point_id": self.point_id,
            "pos": self.pos,
            "owner": self.owner,
            "mark_type": self.mark_type,
            "color": self.color,
            "texture": self.texture,
            "remove_time": self.remove_time
        }

    @staticmethod
    def from_dict(data):
        return MarkPoint(
            data['point_id'],
            data['pos'],
            data['owner'],
            data['mark_type'],
            data['color'],
            data['texture'],
            data['remove_time']
        )