from collections import defaultdict
from contextlib import contextmanager
from typing import Any, Dict, Optional

import colorama

colorama.init()


class Stylist(object):
    styles: Dict[str, str] = {
        "reset": colorama.Style.RESET_ALL,
        "title": colorama.Fore.CYAN + colorama.Style.BRIGHT,
        "subtitle": colorama.Fore.CYAN,
        "success": colorama.Fore.GREEN,
        "danger": colorama.Fore.RED,
    }

    def echo(self, content: str = "", nl: bool = True) -> None:
        print(content, end="\n" if nl else "", flush=True)

    @contextmanager
    def activate(self, style: str) -> Any:
        self.echo(self.styles[style], nl=False)
        try:
            yield self.echo
        finally:
            self.echo(self.styles["reset"], nl=False)

    def draw_checkbox(self, content: str, checked: bool, margin: int = 2) -> None:
        self.echo(" " * margin, nl=False)
        with self.activate("success" if checked else "danger") as echo:
            echo("[{}] ".format("X" if checked else " "), nl=False)
        echo(content, nl=False)

    @contextmanager
    def checkbox(
        self, content: str, content_after: Optional[str] = None, margin: int = 2
    ) -> Any:
        content_after = content_after or content
        space_len = max(0, len(content) - len(content_after))
        self.draw_checkbox(content=content, checked=False, margin=margin)
        yield
        self.echo("\r", nl=False)
        self.draw_checkbox(
            content=content_after + " " * space_len, checked=True, margin=margin
        )
        self.echo("")


class NoopStylist(Stylist):
    styles: Dict[str, str] = defaultdict(str)

    def echo(self, *args, **kwargs):
        pass


stylist = Stylist()
noop_stylist = NoopStylist()
