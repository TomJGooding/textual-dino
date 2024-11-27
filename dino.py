from textual import events
from textual.app import App, ComposeResult, RenderResult
from textual.containers import Container
from textual.geometry import Offset
from textual.reactive import reactive, var
from textual.widget import Widget

GAME_OVER_BANNER = """\
█▀▀ █▀█ ███ ██▀    ▄▀█ █ █ ██▀ █▀█
█▄█ █▀█ █ █ █▄▄    █▄▀ ▀█▀ █▄▄ █▀▄\
"""

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

    is_jumping = var(False)

    def __init__(self) -> None:
        super().__init__()
        self.dy = 0

    def render(self) -> RenderResult:
        return DINO_SPRITE

    def update(self) -> None:
        if self.is_jumping:
            if self.dy > 0 and self.offset.y == 10:
                self.is_jumping = False
            elif self.dy < 0 and self.offset.y == 0:
                self.dy = 1

            self.offset += Offset(0, self.dy)

    def watch_is_jumping(self) -> None:
        if self.is_jumping:
            self.dy = -1
        else:
            self.dy = 0


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

    def update(self) -> None:
        if self.offset.x < 0:
            self.remove()
        else:
            self.offset -= Offset(1, 0)


class Desert(Container):
    DEFAULT_CSS = """
    Desert {
        width: 80;
        height: 15;
        layers: cacti dino;
        border-bottom: wide $foreground;
    }
    """


class Scoreboard(Widget):
    DEFAULT_CSS = """
    Scoreboard {
        width: auto;
        height: auto;
        dock: right;
        margin-right: 3;
        text-style: bold;
    }
    """
    score = reactive(0)
    high_score = reactive(0)

    def __init__(self, high_score: int = 0):
        super().__init__()
        self.high_score = high_score

    def render(self) -> RenderResult:
        if self.high_score == 0:
            return f"{self.score:05}"
        else:
            return f"HI {self.high_score:05}  {self.score:05}"


class GameOver(Widget):
    DEFAULT_CSS = """
    GameOver {
        height: auto;
        dock: top;
        margin-top: 4;
        text-align: center;
        text-style: bold;
    }
    """

    def render(self) -> RenderResult:
        return GAME_OVER_BANNER


class DinosaurGame(App):
    CSS = """
    Screen {
        border: none;
    }
    """

    def __init__(self) -> None:
        super().__init__(ansi_color=True)
        self.game_over = False
        self.high_score: int = 0
        self.time: int = 0
        self.cactus_spawn_rate: int = 60
        self.key: str | None = None

    def compose(self) -> ComposeResult:
        with Desert():
            yield Scoreboard()
            yield Dino()
            yield Cactus()

    def on_mount(self) -> None:
        self.tick = self.set_interval(1 / 30, self.update)

    def on_key(self, event: events.Key) -> None:
        self.key = event.key
        if self.game_over and self.key in ("up", "space"):
            self.restart()

    def update(self) -> None:
        self.time += 1

        # Score
        scoreboard = self.query_one(Scoreboard)
        if self.time % 3 == 0:
            scoreboard.score += 1
            if scoreboard.score > self.high_score:
                self.high_score = scoreboard.score

        # Player controls
        dino = self.query_one(Dino)
        if self.key in ("up", "space"):
            if not dino.is_jumping:
                dino.is_jumping = True

        dino.update()

        # Spawn cactus
        desert = self.query_one(Desert)
        if self.time % self.cactus_spawn_rate == 0:
            desert.mount(Cactus())

        # Update cacti and check collision
        cacti = self.query(Cactus)
        for cactus in cacti:
            if cactus.region.overlaps(dino.region):
                self.tick.pause()
                self.game_over = True
                scoreboard.high_score = self.high_score
                desert.mount(GameOver())
            else:
                cactus.update()

        # Reset key
        self.key = None

    def restart(self) -> None:
        desert = self.query_one(Desert)
        desert.remove_children()

        desert.mount(Scoreboard(self.high_score))
        desert.mount(Dino())
        desert.mount(Cactus())

        self.time = 0
        self.game_over = False
        self.tick.resume()


if __name__ == "__main__":
    game = DinosaurGame()
    game.run(inline=True)
