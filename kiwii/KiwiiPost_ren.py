from dataclasses import dataclass, field
import random

from renpy import config
import renpy.exports as renpy

from game.characters.ICharacter_ren import ICharacter
from game.phone.kiwii.KiwiiComment_ren import KiwiiComment

"""renpy
init python:
"""


@dataclass
class KiwiiPost:
    user: ICharacter
    _image: str
    message: str = ""
    mentions: list[ICharacter] = field(default_factory=list)
    number_likes: int = random.randint(250, 500)
    liked: bool = False
    comments: list[KiwiiComment] = field(default_factory=list)
    pending_comments: list[KiwiiComment] = field(default_factory=list)

    @property
    def image(self) -> str:
        try:
            self._image
        except AttributeError:
            self._image = self.__dict__.get("image", "")

        if (
            not (renpy.has_image(self._image) or renpy.loadable(self._image))
            and not config.developer
        ):
            return "#fff"

        return self._image

    @image.setter
    def image(self, value: str) -> None:
        self._image = value

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}({self.user}, {self.message}, {self.comments})"
        )

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, KiwiiPost):
            return NotImplemented

        return (
            self.user == __value.user
            and self.image == __value.image
            and self.message == __value.message
        )
