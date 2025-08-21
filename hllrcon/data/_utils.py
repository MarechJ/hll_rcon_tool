from collections.abc import Callable, Hashable
from typing import TYPE_CHECKING, Any, ClassVar, Generic, Never, Self, cast

from pydantic import BaseModel, ConfigDict, PrivateAttr
from typing_extensions import TypeVar

T = TypeVar("T")
H = TypeVar("H", bound=Hashable)
R = TypeVar("R", default=Never)


class class_cached_property(Generic[T]):  # noqa: N801
    def __init__(self, func: Callable[[type], T]) -> None:
        if TYPE_CHECKING or not isinstance(func, classmethod):  # pragma: no cover
            self.func = func
        else:
            self.func = func.__func__
        self.resolved: bool = False
        self.value: T | None = None

    def __get__(self, instance: T | None, owner: type) -> T:
        if not self.resolved:
            self.resolve(owner)
        return self.value  # type: ignore[return-value]

    def resolve(self, cls: type) -> None:
        self.value = self.func(cls)
        self.resolved = True


class IndexedBaseModel(BaseModel, Generic[H, R]):
    model_config = ConfigDict(
        ignored_types=(class_cached_property,),
        frozen=True,
    )
    _lookup_map: ClassVar[dict[Any, "IndexedBaseModel[Any, Any]"]]

    if TYPE_CHECKING:
        id: H = PrivateAttr()

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:  # noqa: ANN401
        if (
            cls.model_fields
            and "id" not in cls.model_fields
            and "id" not in cls.model_computed_fields
            and "id" not in cls.__dict__
        ):
            msg = f"{cls.__name__} must define an 'id' field."
            raise TypeError(msg)

        cls._lookup_map = {}

        for value in cls.__dict__.values():
            if isinstance(value, class_cached_property):
                value.resolve(cls)

    @classmethod
    def _lookup_register(cls, id_: H, instance: Self) -> None:
        if id_ in cls._lookup_map:
            msg = f"{cls.__name__} with ID {id_} already exists."
            raise ValueError(msg)

        cls._lookup_map[id_] = instance

    @classmethod
    def _lookup_fallback(cls, id_: H) -> Self | R:
        msg = f"{cls.__name__} with ID {id_} not found."
        raise ValueError(msg)

    def model_post_init(self, context: Any) -> None:  # noqa: ANN401, ARG002
        self._lookup_register(self.id, self)  # type: ignore[attr-defined]

    @classmethod
    def by_id(cls, id_: H) -> Self | R:
        """Look up a model by its identifier.

        Parameters
        ----------
        id_ : H
            The identifier of the model to look up.

        Returns
        -------
        Self | R
            The model instance with the given identifier.

        Raises
        ------
        ValueError
            If no model with the given identifier exists.

        """
        if instance := cls._lookup_map.get(id_):
            return cast("Self", instance)

        return cls._lookup_fallback(id_)

    @classmethod
    def all(cls) -> list[Self]:
        """Return all known instances of the model.

        Returns
        -------
        list[Self]
            A list of all model instances.

        """
        return list(cls._lookup_map.values())  # type: ignore[return-value]


class CaseInsensitiveIndexedBaseModel(IndexedBaseModel[str, R]):
    id: str

    @classmethod
    def by_id(cls, id_: str) -> Self | R:
        return super().by_id(id_.lower())

    @classmethod
    def _lookup_register(cls, id_: str, instance: Self) -> None:
        return super()._lookup_register(id_.lower(), instance)
