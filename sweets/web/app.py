"""Flask web application for Vestaboard control."""

from flask import Flask, render_template, request, redirect, url_for, jsonify, flash

from sweets.config import load_config
from sweets.core.api import CloudClient, LocalClient, RateLimitError
from sweets.scheduler import Scheduler
from sweets.modes import get_all_modes

app = Flask(__name__)
app.secret_key = "sweets-vestaboard"  # For flash messages

# Global scheduler instance (initialized in main)
scheduler: Scheduler | None = None


def get_scheduler() -> Scheduler:
    """Get or create the scheduler instance."""
    global scheduler
    if scheduler is None:
        raise RuntimeError("Scheduler not initialized. Call main() first.")
    return scheduler


@app.route("/")
def index():
    """Dashboard homepage."""
    sched = get_scheduler()
    status = sched.get_status()
    modes = get_all_modes()

    # Get current board display
    board_display = None
    if sched.get_last_board() is not None:
        board_display = sched.get_last_board().to_array()

    return render_template(
        "index.html",
        status=status,
        modes=modes,
        board=board_display,
        board_rows=sched.board_rows,
        board_cols=sched.board_cols,
    )


@app.route("/status")
def status():
    """JSON status endpoint."""
    sched = get_scheduler()
    return jsonify(sched.get_status())


@app.route("/message", methods=["POST"])
def send_message():
    """Send a custom message to the board."""
    text = request.form.get("text", "").strip()
    if text:
        sched = get_scheduler()
        try:
            sched.send_message(text)
        except RateLimitError:
            flash("Rate limited - please wait ~15 seconds between messages", "error")
    return redirect(url_for("index"))


@app.route("/mode/<slug>", methods=["POST"])
def activate_mode(slug: str):
    """Switch to a different mode."""
    sched = get_scheduler()
    try:
        sched.start(slug)
    except KeyError:
        pass  # Invalid mode, just redirect
    return redirect(url_for("index"))


@app.route("/stop", methods=["POST"])
def stop_mode():
    """Stop the current mode."""
    sched = get_scheduler()
    sched.stop()
    return redirect(url_for("index"))


def main():
    """Entry point for the web application."""
    global scheduler

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

    # Run Flask (use_reloader=False to avoid duplicate scheduler instances)
    app.run(host=config.web_host, port=config.web_port, debug=True, use_reloader=False)


if __name__ == "__main__":
    main()
