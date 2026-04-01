import threading
import time

from vulcano.app import VulcanoApp
from vulcano.themes import MonokaiTheme


app = VulcanoApp("async_output_demo")


@app.command
def start_background(interval=1, ticks=5):
    """Start a background task that prints while the REPL remains active.

    :param int interval: Seconds to wait between messages.
    :param int ticks: Number of messages to print.
    """

    def worker():
        for i in range(ticks):
            time.sleep(interval)
            print("[background] tick {}".format(i))

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    return "Background task started"


@app.command
def hello(name="User"):
    """Simple foreground command for testing prompt redraw.

    :param str name: Name to greet.
    """
    return "Hello {}!".format(name)


if __name__ == "__main__":
    app.run(theme=MonokaiTheme)
