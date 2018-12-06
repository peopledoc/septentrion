from __future__ import print_function

from collections import defaultdict
from contextlib import contextmanager

import colorama

colorama.init()


class Stylist(object):
    styles = {
        "reset": colorama.Style.RESET_ALL,
        "title": colorama.Fore.CYAN + colorama.Style.BRIGHT,
        "subtitle": colorama.Fore.CYAN,
        "success": colorama.Fore.GREEN,
        "danger": colorama.Fore.RED,
    }

    def echo(self, content="", nl=True):
        print(content, end="\n" if nl else "", flush=True)

    @contextmanager
    def activate(self, style):
        self.echo(self.styles[style], nl=False)
        try:
            yield self.echo
        finally:
            self.echo(self.styles["reset"], nl=False)

    def draw_checkbox(self, content, checked, margin=2):
        self.echo(" " * margin, nl=False)
        with self.activate("success" if checked else "danger") as echo:
            echo("[{}] ".format("X" if checked else " "), nl=False)
        echo(content, nl=False)

    @contextmanager
    def checkbox(self, content, content_after=None, margin=2):
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
    styles = defaultdict(str)

    def echo(self, *args, **kwargs):
        pass


stylist = Stylist()
noop_stylist = NoopStylist()
