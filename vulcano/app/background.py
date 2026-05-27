"""Background task management for structured async work in Vulcano.

This module provides a registry-based approach to tracking background tasks,
managing their output, and displaying their status in the REPL.
"""

from __future__ import annotations

import queue
import threading
import time
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum


class TaskStatus(Enum):
    """Enumeration of possible task states."""

    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class BackgroundTask:
    """Represents a single background task with state and output."""

    task_id: str
    name: str
    thread: threading.Thread
    status: TaskStatus
    started_at: float
    completed_at: float | None = None
    error: Exception | None = None


class BackgroundTaskManager:
    """Central registry for managing background tasks and their output.

    This manager tracks running tasks, queues their output to avoid
    corrupting the REPL prompt, and provides status information for
    display in toolbars or other UI elements.
    """

    def __init__(self) -> None:
        """Initialize the background task manager."""
        self._tasks: OrderedDict[str, BackgroundTask] = OrderedDict()
        self._output_queue: queue.Queue[tuple[str, str]] = queue.Queue()
        self._lock = threading.Lock()
        self._next_task_id = 0
        self._ui_invalidate_callback: Callable[[], None] | None = None

    def register_task(self, name: str, thread: threading.Thread) -> str:
        """Register a new background task.

        Args:
            name (str): Human-readable task name.
            thread (threading.Thread): The thread executing the task.

        Returns:
            str: Unique task ID.
        """
        with self._lock:
            task_id = "task_{}".format(self._next_task_id)
            self._next_task_id += 1
            task = BackgroundTask(
                task_id=task_id,
                name=name,
                thread=thread,
                status=TaskStatus.RUNNING,
                started_at=time.time(),
            )
            self._tasks[task_id] = task
            return task_id

    def set_ui_invalidate_callback(self, callback: Callable[[], None]) -> None:
        """Set a callback to trigger UI redraw when output is enqueued.

        Args:
            callback: Function to call to invalidate/redraw the UI.
        """
        self._ui_invalidate_callback = callback

    def mark_completed(self, task_id: str) -> None:
        """Mark a task as completed.

        Args:
            task_id (str): Task identifier.
        """
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id].status = TaskStatus.COMPLETED
                self._tasks[task_id].completed_at = time.time()
        # Trigger UI refresh to update toolbar
        if self._ui_invalidate_callback:
            self._ui_invalidate_callback()

    def mark_failed(self, task_id: str, error: Exception) -> None:
        """Mark a task as failed.

        Args:
            task_id (str): Task identifier.
            error (Exception): Exception that caused the failure.
        """
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id].status = TaskStatus.FAILED
                self._tasks[task_id].completed_at = time.time()
                self._tasks[task_id].error = error
        # Trigger UI refresh to update toolbar
        if self._ui_invalidate_callback:
            self._ui_invalidate_callback()

    def enqueue_output(self, task_id: str, message: str) -> None:
        """Enqueue output from a background task.

        Args:
            task_id (str): Task identifier.
            message (str): Message to display.
        """
        self._output_queue.put((task_id, message))
        # Trigger UI refresh to display output immediately
        if self._ui_invalidate_callback:
            self._ui_invalidate_callback()

    def get_queued_output(self) -> list[tuple[str, str]]:
        """Retrieve all queued output messages.

        Returns:
            list[tuple[str, str]]: List of (task_id, message) tuples.
        """
        messages = []
        while not self._output_queue.empty():
            try:
                messages.append(self._output_queue.get_nowait())
            except queue.Empty:
                break
        return messages

    def get_active_tasks(self) -> list[BackgroundTask]:
        """Return a list of currently running tasks.

        Returns:
            list[BackgroundTask]: Active tasks.
        """
        with self._lock:
            return [
                task
                for task in self._tasks.values()
                if task.status == TaskStatus.RUNNING
            ]

    def get_all_tasks(self) -> list[BackgroundTask]:
        """Return all registered tasks.

        Returns:
            list[BackgroundTask]: All tasks regardless of status.
        """
        with self._lock:
            return list(self._tasks.values())

    def wait_for_all_tasks(self, timeout: float | None = None) -> None:
        """Wait for all registered tasks to complete.

        This is primarily for CLI mode to ensure the process doesn't exit
        before background work finishes.

        Args:
            timeout (float | None): Maximum time to wait in seconds.
        """
        with self._lock:
            threads = [task.thread for task in self._tasks.values()]

        for thread in threads:
            if thread.is_alive():
                thread.join(timeout=timeout)

    def has_active_tasks(self) -> bool:
        """Check if any tasks are currently running.

        Returns:
            bool: True if at least one task is running.
        """
        with self._lock:
            return any(
                task.status == TaskStatus.RUNNING for task in self._tasks.values()
            )

    def clear_completed_tasks(self) -> None:
        """Remove completed and failed tasks from the registry."""
        with self._lock:
            self._tasks = OrderedDict(
                (tid, task)
                for tid, task in self._tasks.items()
                if task.status == TaskStatus.RUNNING
            )

    def get_status_summary(self, include_names: bool = False) -> str:
        """Return a formatted status summary for display.

        Args:
            include_names (bool): Include task names in the summary.

        Returns:
            str: Status summary (e.g., "2 tasks running: task1, task2").
        """
        with self._lock:
            active_tasks = [
                task
                for task in self._tasks.values()
                if task.status == TaskStatus.RUNNING
            ]
            active_count = len(active_tasks)
            if active_count == 0:
                return ""

            # Build base count message
            if active_count == 1:
                base_msg = "1 task running"
            else:
                base_msg = "{} tasks running".format(active_count)

            # Optionally append task names
            if include_names and active_tasks:
                task_names = [task.name for task in active_tasks]
                # Truncate long names and limit to 3 tasks
                display_names = [
                    name[:15] + "..." if len(name) > 15 else name
                    for name in task_names[:3]
                ]
                names_str = ", ".join(display_names)
                if active_count > 3:
                    names_str += ", ..."
                return "{}: {}".format(base_msg, names_str)

            return base_msg
