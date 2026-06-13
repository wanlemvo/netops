from __future__ import annotations

from dataclasses import dataclass
import shutil
import sys

from prompt_toolkit import Application
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.output import DummyOutput

from netops.services import EvaluationService, InteractionService, OpenLoopService, PeopleService, SuggestionService
from netops.storage import NetOpsRepository, connect
from netops.tui.screens import has_clipped_rows, visible_rows
from netops.tui.state import ScreenName, TuiState
from netops.tui.theme import CYBERPUNK_STYLE, FOOTER, HEADER


@dataclass(slots=True)
class NetOpsTuiServices:
    repository: NetOpsRepository
    people: PeopleService
    interactions: InteractionService
    loops: OpenLoopService
    suggestions: SuggestionService
    evaluations: EvaluationService


def create_services() -> NetOpsTuiServices:
    repository = NetOpsRepository(connect())
    people = PeopleService(repository)
    interactions = InteractionService(repository, people)
    loops = OpenLoopService(repository, people)
    suggestions = SuggestionService(repository, people)
    evaluations = EvaluationService(repository, people)
    return NetOpsTuiServices(repository, people, interactions, loops, suggestions, evaluations)


class NetOpsTui:
    def __init__(self, services: NetOpsTuiServices | None = None) -> None:
        self.services = services or create_services()
        self.state = TuiState(self.services)
        self.control = FormattedTextControl(self.render_formatted_text, focusable=True)
        self.application = Application(
            layout=Layout(Window(content=self.control, always_hide_cursor=False)),
            key_bindings=self.create_key_bindings(),
            style=CYBERPUNK_STYLE,
            full_screen=True,
            mouse_support=False,
            output=None if sys.stdout.isatty() else DummyOutput(),
        )

    def create_key_bindings(self) -> KeyBindings:
        bindings = KeyBindings()

        @bindings.add("up")
        def move_up(event) -> None:
            self.state.move_up()
            event.app.invalidate()

        @bindings.add("down")
        def move_down(event) -> None:
            self.state.move_down()
            event.app.invalidate()

        @bindings.add("enter")
        def activate(event) -> None:
            result = self.state.activate()
            if result.exit_requested:
                event.app.exit()
                return
            event.app.invalidate()

        @bindings.add("escape")
        def escape(event) -> None:
            self.state.escape()
            event.app.invalidate()

        @bindings.add("backspace")
        def backspace(event) -> None:
            self.state.backspace()
            event.app.invalidate()

        @bindings.add("tab")
        def next_field(event) -> None:
            self.state.tab_field()
            event.app.invalidate()

        @bindings.add("s-tab")
        def previous_field(event) -> None:
            self.state.tab_field(backwards=True)
            event.app.invalidate()

        @bindings.add("c-c")
        def ctrl_c(event) -> None:
            event.app.exit()

        @bindings.add("<any>")
        def any_key(event) -> None:
            data = event.key_sequence[0].data
            if self.state.current.name in {
                ScreenName.ADD_PERSON_FORM,
                ScreenName.LOG_INTERACTION_FORM,
                ScreenName.EDIT_FIELD_FORM,
                ScreenName.RAW_NOTE_FORM,
                ScreenName.CONTACT_FORM,
                ScreenName.OPEN_LOOP_FORM,
            } and data and data.isprintable():
                self.state.enter_text(data)
                event.app.invalidate()

        return bindings

    def render_formatted_text(self) -> FormattedText:
        screen = self.state.current
        fragments: list[tuple[str, str]] = []
        if screen.name == ScreenName.MAIN_MENU:
            fragments.append(("class:logo", f"{HEADER}\n"))
        fragments.extend(
            [
                ("class:title", "NETOPS // RELATIONSHIP OPS TERMINAL\n"),
                ("class:border", "=" * 72 + "\n"),
                ("class:subtitle", f"{screen.title}\n\n"),
            ]
        )

        row_height = self.visible_item_height(screen)
        rows = visible_rows(screen, height=row_height)
        clipped = has_clipped_rows(screen, height=row_height)
        if len(screen.items) <= row_height:
            indexed_rows = list(enumerate(rows))
        else:
            screen.clamp_selection()
            start = max(0, min(screen.selected_index, len(screen.items) - row_height))
            indexed_rows = list(enumerate(rows, start=start))

        def append_items() -> None:
            for absolute_index, item in indexed_rows:
                is_text_row = item.kind == "noop"
                marker = " " if is_text_row else (">" if absolute_index == screen.selected_index else " ")
                style = "class:field" if is_text_row else ("class:selected" if absolute_index == screen.selected_index else "")
                if not item.enabled:
                    style = "class:disabled"
                hint = f"  // {item.hint}" if item.hint else ""
                fragments.append((style, f"{marker} {item.label}{hint}\n"))
            if clipped:
                fragments.append(("class:hint", "... more items hidden; keep moving to scroll ...\n"))

        def append_body() -> None:
            for line in screen.body:
                style = "class:error" if line.startswith("!") else "class:field"
                fragments.append((style, f"{line}\n"))

        if screen.name != ScreenName.DOSSIER:
            append_body()
        if screen.name != ScreenName.DOSSIER and screen.body and screen.items:
            fragments.append(("", "\n"))
        append_items()

        fragments.extend(
            [
                ("", "\n"),
                ("class:status", f"{screen.status}\n"),
                ("class:border", "-" * 72 + "\n"),
                ("class:hint", f"{FOOTER}\n"),
            ]
        )
        return FormattedText(fragments)

    def visible_item_height(self, screen) -> int:
        if screen.name != ScreenName.DOSSIER:
            return 12
        terminal = shutil.get_terminal_size(fallback=(80, 24))
        reserved_rows = 8
        return max(8, terminal.lines - reserved_rows)

    def run(self) -> None:
        self.application.run()

    def render_text_for_tests(self) -> str:
        return "".join(text for _, text in self.render_formatted_text())
