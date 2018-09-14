import pytest
from west.style import noop_stylist
from west.style import stylist

CHECKED = "\x1b[32m[X] \x1b[0m"
NOT_CHECKED = "\x1b[31m[ ] \x1b[0m"


@pytest.mark.parametrize("expected,newline", [("foo\n", True), ("foo", False)])
def test_stylist_echo(capsys, expected, newline):
    stylist.echo("foo", nl=newline)
    out, _ = capsys.readouterr()
    assert out == expected


def test_noop_stylist_echo(capsys):
    # it should does nothing
    noop_stylist.echo("foo")
    out, _ = capsys.readouterr()
    assert out == ""


@pytest.mark.parametrize(
    "expected,checked,margin",
    [
        ("  {}foo".format(CHECKED), True, 2),
        ("  {}foo".format(NOT_CHECKED), False, 2),
        ("    {}foo".format(NOT_CHECKED), False, 4),
    ],
)
def test_draw_checkbox(capsys, expected, checked, margin):
    stylist.draw_checkbox("foo", checked=checked, margin=margin)
    out, _ = capsys.readouterr()
    assert out == expected


def test_checkbox(capsys):
    with stylist.checkbox(content="Faking ...", content_after="Faked"):
        out, _ = capsys.readouterr()
        assert out == "  {}Faking ...".format(NOT_CHECKED)
    out, _ = capsys.readouterr()
    assert out == "\r  {}Faked     \n".format(CHECKED)


def test_activate(capsys):
    with stylist.activate("title") as echo:
        echo("foo")
        out, _ = capsys.readouterr()
        assert out == "\x1b[36m\x1b[1mfoo\n"
