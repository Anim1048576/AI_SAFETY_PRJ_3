"""FA-003 placeholder.

PRD상 MVP 범위 밖이라 런타임에는 연결하지 않는다.
이미지의 방향성만 살려서 나중에 확장할 수 있게 틀만 남겨둔다.
"""


class FightDet:
    def kps(self):
        raise NotImplementedError("FA-003 is not enabled in MVP")

    def count(self):
        raise NotImplementedError("FA-003 is not enabled in MVP")

    def speed(self):
        raise NotImplementedError("FA-003 is not enabled in MVP")

    def hot(self):
        raise NotImplementedError("FA-003 is not enabled in MVP")

    def tick(self):
        raise NotImplementedError("FA-003 is not enabled in MVP")
