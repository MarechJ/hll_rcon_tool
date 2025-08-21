# ruff: noqa: N802


from ._utils import IndexedBaseModel, class_cached_property


class Team(IndexedBaseModel[int]):
    id: int
    name: str

    @class_cached_property
    @classmethod
    def ALLIES(cls) -> "Team":
        return cls(id=1, name="Allies")

    @class_cached_property
    @classmethod
    def AXIS(cls) -> "Team":
        return cls(id=2, name="Axis")
