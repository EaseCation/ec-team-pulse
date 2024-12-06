# -*- coding: utf-8 -*-

class MarkPoint(object):

    def __init__(self, pos, mark_type, color, texture):
        self.pos = pos  # type: tuple[float, float, float]
        self.mark_type = mark_type  # type: str
        self.color = color  # type: tuple[int, int, int]
        self.texture = texture  # type: str

