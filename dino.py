from textual import events
from textual.app import App, ComposeResult, RenderResult
from textual.containers import Container
from textual.geometry import Offset
from textual.widget import Widget

DINO_SPRITE = """\
   █▀██
█▄ ██▀▀
▀████▀ 
  █▀█  \
"""

CACTUS_SPRITE = """\
▄ ██ ▄
█ ██▄█
▀▀██  
  ██  \
"""


class Dino(Widget):
    DEFAULT_CSS = """
    Dino {
        width: auto;
        height: auto;
        layer: dino;
        position: absolute;
        offset: 3 10;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self.is_jumping = False
        self.dy = 0

    def render(self) -> RenderResult:
        return DINO_SPRITE


class Cactus(Widget):
    DEFAULT_CSS = """
    Cactus {
        width: auto;
        height: auto;
        layer: cacti;
        position: absolute;
        offset: 80 10;
    }
    """

    def render(self) -> RenderResult:
        return CACTUS_SPRITE


class Desert(Container):
    DEFAULT_CSS = """
    Desert {
        width: 80;
        height: 15;
        layers: cacti dino;
        border-bottom: wide $foreground;
    }
    """


class DinosaurGame(App):
    CSS = """
    Screen {
        border: none;
    }
    """

    def __init__(self) -> None:
        super().__init__(ansi_color=True)
        self.time: int = 0
        self.cactus_spawn_rate: int = 60
        self.key: str | None = None

    def compose(self) -> ComposeResult:
        with Desert():
            yield Dino()
            yield Cactus()

    def on_mount(self) -> None:
        self.tick = self.set_interval(1 / 30, self.update)

    def on_key(self, event: events.Key) -> None:
        self.key = event.key

    def update(self) -> None:
        self.time += 1

        # Player controls
        dino = self.query_one(Dino)
        if self.key in ("up", "space"):
            if not dino.is_jumping:
                dino.is_jumping = True
                dino.dy = -1

        if dino.is_jumping:
            if dino.dy > 0 and dino.offset.y == 10:
                dino.is_jumping = False
                dino.dy = 0
            elif dino.dy < 0 and dino.offset.y == 0:
                dino.dy = 1

            dino.offset += Offset(0, dino.dy)

        # Spawn cactus
        desert = self.query_one(Desert)
        if self.time % self.cactus_spawn_rate == 0:
            desert.mount(Cactus())

        # Update cacti
        cacti = self.query(Cactus)
        for cactus in cacti:
            if cactus.offset.x < 0:
                cactus.remove()
            else:
                cactus.offset -= Offset(1, 0)

        # Reset key
        self.key = None


if __name__ == "__main__":
    game = DinosaurGame()
    game.run(inline=True)