"""Textual TUI application for Vestaboard control."""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, Label, Static, Select
from textual.binding import Binding

from sweets.config import load_config
from sweets.core.api import CloudClient, LocalClient
from sweets.core.characters import codes_to_text
from sweets.scheduler import Scheduler
from sweets.modes import get_all_modes
from sweets.modes.illustrations import ILLUSTRATIONS


class BoardDisplay(Static):
    """Widget displaying the Vestaboard grid."""

    def __init__(self, rows: int = 6, cols: int = 22) -> None:
        super().__init__()
        self._board: list[list[int]] | None = None
        self._rows = rows
        self._cols = cols

    def set_board(self, board: list[list[int]] | None) -> None:
        """Update the displayed board."""
        self._board = board
        self.refresh()

    def render(self) -> str:
        """Render the board as text."""
        if self._board is None:
            return "\n".join(["." * self._cols] * self._rows)

        lines = []
        for row in self._board:
            line = ""
            for code in row:
                if code == 0:
                    line += "."
                elif 1 <= code <= 26:
                    line += chr(64 + code)
                elif 27 <= code <= 35:
                    line += str(code - 26)
                elif code == 36:
                    line += "0"
                elif 63 <= code <= 70:
                    colors = ["R", "O", "Y", "G", "B", "V", "W", "K"]
                    line += colors[code - 63]
                else:
                    line += "?"
            lines.append(line)
        return "\n".join(lines)


class SweetsApp(App):
    """Textual application for Vestaboard control."""

    CSS = """
    Screen {
        layout: grid;
        grid-size: 2;
        grid-columns: 2fr 1fr;
    }

    #board-container {
        height: 100%;
        border: solid green;
        padding: 1;
    }

    #controls {
        height: 100%;
        border: solid blue;
        padding: 1;
    }

    BoardDisplay {
        height: auto;
        padding: 1;
        background: $surface;
        text-style: bold;
        text-align: center;
    }

    #status {
        height: auto;
        padding: 1;
        margin-bottom: 1;
    }

    Input {
        margin-bottom: 1;
    }

    Button {
        margin: 1 0;
        width: 100%;
    }

    #stop-btn {
        background: red;
    }

    #illustration-select {
        display: none;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("m", "focus_mode", "Mode"),
        Binding("t", "focus_text", "Text"),
        Binding("s", "stop_mode", "Stop"),
    ]

    def __init__(self, scheduler: Scheduler, board_rows: int = 6, board_cols: int = 22) -> None:
        super().__init__()
        self.scheduler = scheduler
        self.board_rows = board_rows
        self.board_cols = board_cols

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        with Container(id="board-container"):
            yield Label("Board Preview", id="board-label")
            yield BoardDisplay(rows=self.board_rows, cols=self.board_cols)
            yield Label("", id="status")

        with Container(id="controls"):
            yield Label("Send Message")
            yield Input(placeholder="Type message...", id="message-input")
            yield Button("Send", id="send-btn", variant="primary")

            yield Label("Mode Control")
            modes = get_all_modes()
            options = [(mode_cls.name, slug) for slug, mode_cls in modes.items()]
            yield Select(options, id="mode-select", prompt="Select mode")

            # Illustration selector (hidden by default)
            ill_options = [(ill.name, slug) for slug, ill in ILLUSTRATIONS.items()]
            yield Select(ill_options, id="illustration-select", prompt="Select illustration")

            yield Button("Activate", id="activate-btn", variant="success")
            yield Button("Stop", id="stop-btn", variant="error")

        yield Footer()

    def on_mount(self) -> None:
        """Called when app is mounted."""
        self.update_display()
        self.set_interval(1, self.update_display)

    def update_display(self) -> None:
        """Update board display and status."""
        board_widget = self.query_one(BoardDisplay)
        status_label = self.query_one("#status", Label)

        last_board = self.scheduler.get_last_board()
        if last_board:
            board_widget.set_board(last_board.to_array())

        status = self.scheduler.get_status()
        mode_name = status.get("mode_name") or "None"
        last_update = status.get("last_update") or "Never"
        status_label.update(f"Mode: {mode_name} | Updated: {last_update}")

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle select widget changes."""
        if event.select.id == "mode-select":
            ill_select = self.query_one("#illustration-select", Select)
            if event.value == "illustrations":
                ill_select.styles.display = "block"
            else:
                ill_select.styles.display = "none"
        elif event.select.id == "illustration-select":
            if self.scheduler.active_mode and hasattr(self.scheduler.active_mode, "set_illustration"):
                self.scheduler.active_mode.set_illustration(str(event.value))
                self.scheduler.force_update()
                self.update_display()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "send-btn":
            input_widget = self.query_one("#message-input", Input)
            text = input_widget.value.strip()
            if text:
                self.scheduler.send_message(text)
                input_widget.value = ""
                self.update_display()

        elif event.button.id == "activate-btn":
            select = self.query_one("#mode-select", Select)
            if select.value and select.value != Select.BLANK:
                self.scheduler.start(str(select.value))
                # Show/hide illustration selector
                ill_select = self.query_one("#illustration-select", Select)
                if select.value == "illustrations":
                    ill_select.styles.display = "block"
                else:
                    ill_select.styles.display = "none"
                self.update_display()

        elif event.button.id == "stop-btn":
            self.scheduler.stop()
            self.update_display()

    def action_focus_mode(self) -> None:
        """Focus the mode selector."""
        self.query_one("#mode-select").focus()

    def action_focus_text(self) -> None:
        """Focus the text input."""
        self.query_one("#message-input").focus()

    def action_stop_mode(self) -> None:
        """Stop the current mode."""
        self.scheduler.stop()
        self.update_display()


def main():
    """Entry point for the TUI application."""
    config = load_config()

    # Create API client
    if config.api_type == "local":
        client = LocalClient(
            api_key=config.local_api_key or "",
            host=config.api_host,
        )
    else:
        client = CloudClient(api_token=config.cloud_api_token)

    # Create scheduler
    scheduler = Scheduler(
        client,
        mode_settings=config.modes,
        board_rows=config.board_rows,
        board_cols=config.board_cols,
    )

    # Start default mode if configured
    if config.default_mode:
        try:
            scheduler.start(config.default_mode)
        except KeyError:
            pass

    # Run app
    app = SweetsApp(scheduler, board_rows=config.board_rows, board_cols=config.board_cols)
    app.run()


if __name__ == "__main__":
    main()
