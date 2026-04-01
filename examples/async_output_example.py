import threading
import time

from vulcano.app import VulcanoApp
from vulcano.themes import MonokaiTheme

app = VulcanoApp("async_output_demo")


@app.command
def start_background(interval=1, ticks=5):
    """Start a background task that prints while the REPL remains active.

    Uses the background task manager for structured output and status tracking.

    :param int interval: Seconds to wait between messages.
    :param int ticks: Number of messages to print.
    """

    def worker(task_id):
        try:
            for i in range(ticks):
                time.sleep(interval)
                app.background_tasks.enqueue_output(task_id, "tick {}".format(i))
            app.background_tasks.mark_completed(task_id)
        except Exception as e:
            app.background_tasks.mark_failed(task_id, e)

    thread = threading.Thread(target=worker, args=(None,), daemon=True)
    # Register the task before starting the thread
    task_id = app.background_tasks.register_task("background_{}".format(ticks), thread)
    # Update the thread args with the actual task_id
    thread = threading.Thread(target=worker, args=(task_id,), daemon=True)
    # Re-register with the correct thread
    app.background_tasks._tasks[task_id].thread = thread
    thread.start()
    return "Background task started ({})".format(task_id)


@app.command
def hello(name="User"):
    """Simple foreground command for testing prompt redraw.

    :param str name: Name to greet.
    """
    return "Hello {}!".format(name)


if __name__ == "__main__":
    app.run(theme=MonokaiTheme)
