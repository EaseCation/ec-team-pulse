# -*- coding: utf-8 -*-

class MarkPoint(object):

    def __init__(self, pos, color, texture):
        self.pos = pos  # type: tuple[float, float, float]
        self.color = color  # type: tuple[int, int, int]
        self.texture = texture  # type: str

