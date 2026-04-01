"""Tests for background task management."""

import queue
import threading
import time
import unittest
import unittest.mock

from vulcano.app.background import (
    BackgroundTaskManager,
    TaskStatus,
)


class BackgroundTaskManagerTest(unittest.TestCase):
    """Test the BackgroundTaskManager class."""

    def setUp(self):
        """Set up a fresh task manager for each test."""
        self.manager = BackgroundTaskManager()

    def test_register_task_assigns_unique_id(self):
        """Task registration assigns unique sequential IDs."""

        def dummy_worker():
            pass

        thread1 = threading.Thread(target=dummy_worker)
        thread2 = threading.Thread(target=dummy_worker)

        task_id1 = self.manager.register_task("task1", thread1)
        task_id2 = self.manager.register_task("task2", thread2)

        self.assertEqual(task_id1, "task_0")
        self.assertEqual(task_id2, "task_1")

    def test_register_task_creates_running_task(self):
        """Newly registered tasks start with RUNNING status."""

        def dummy_worker():
            pass

        thread = threading.Thread(target=dummy_worker)
        task_id = self.manager.register_task("test_task", thread)

        tasks = self.manager.get_all_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].status, TaskStatus.RUNNING)
        self.assertEqual(tasks[0].task_id, task_id)

    def test_mark_completed_updates_status(self):
        """Marking a task completed updates its status and timestamp."""

        def dummy_worker():
            pass

        thread = threading.Thread(target=dummy_worker)
        task_id = self.manager.register_task("test_task", thread)

        self.manager.mark_completed(task_id)

        tasks = self.manager.get_all_tasks()
        self.assertEqual(tasks[0].status, TaskStatus.COMPLETED)
        self.assertIsNotNone(tasks[0].completed_at)

    def test_mark_failed_updates_status_and_error(self):
        """Marking a task failed captures the exception."""

        def dummy_worker():
            pass

        thread = threading.Thread(target=dummy_worker)
        task_id = self.manager.register_task("test_task", thread)

        error = ValueError("test error")
        self.manager.mark_failed(task_id, error)

        tasks = self.manager.get_all_tasks()
        self.assertEqual(tasks[0].status, TaskStatus.FAILED)
        self.assertEqual(tasks[0].error, error)
        self.assertIsNotNone(tasks[0].completed_at)

    def test_enqueue_and_get_output(self):
        """Output can be enqueued and retrieved."""
        task_id = "task_0"
        self.manager.enqueue_output(task_id, "message 1")
        self.manager.enqueue_output(task_id, "message 2")

        output = self.manager.get_queued_output()
        self.assertEqual(len(output), 2)
        self.assertEqual(output[0], (task_id, "message 1"))
        self.assertEqual(output[1], (task_id, "message 2"))

        # Queue should be empty after retrieval
        output = self.manager.get_queued_output()
        self.assertEqual(len(output), 0)

    def test_get_active_tasks_filters_running(self):
        """get_active_tasks returns only tasks with RUNNING status."""

        def dummy_worker():
            pass

        thread1 = threading.Thread(target=dummy_worker)
        thread2 = threading.Thread(target=dummy_worker)
        thread3 = threading.Thread(target=dummy_worker)

        task_id1 = self.manager.register_task("task1", thread1)
        task_id2 = self.manager.register_task("task2", thread2)
        task_id3 = self.manager.register_task("task3", thread3)

        self.manager.mark_completed(task_id1)
        self.manager.mark_failed(task_id2, ValueError("error"))

        active = self.manager.get_active_tasks()
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].task_id, task_id3)

    def test_has_active_tasks(self):
        """has_active_tasks returns True when tasks are running."""
        self.assertFalse(self.manager.has_active_tasks())

        def dummy_worker():
            pass

        thread = threading.Thread(target=dummy_worker)
        task_id = self.manager.register_task("task", thread)

        self.assertTrue(self.manager.has_active_tasks())

        self.manager.mark_completed(task_id)
        self.assertFalse(self.manager.has_active_tasks())

    def test_clear_completed_tasks(self):
        """clear_completed_tasks removes non-running tasks."""

        def dummy_worker():
            pass

        thread1 = threading.Thread(target=dummy_worker)
        thread2 = threading.Thread(target=dummy_worker)
        thread3 = threading.Thread(target=dummy_worker)

        task_id1 = self.manager.register_task("task1", thread1)
        task_id2 = self.manager.register_task("task2", thread2)
        task_id3 = self.manager.register_task("task3", thread3)

        self.manager.mark_completed(task_id1)
        self.manager.mark_failed(task_id2, ValueError("error"))

        self.manager.clear_completed_tasks()

        all_tasks = self.manager.get_all_tasks()
        self.assertEqual(len(all_tasks), 1)
        self.assertEqual(all_tasks[0].task_id, task_id3)

    def test_get_status_summary(self):
        """get_status_summary returns appropriate text."""
        # No tasks
        self.assertEqual(self.manager.get_status_summary(), "")

        def dummy_worker():
            pass

        # One task
        thread1 = threading.Thread(target=dummy_worker)
        self.manager.register_task("task1", thread1)
        self.assertEqual(self.manager.get_status_summary(), "1 task running")

        # Multiple tasks
        thread2 = threading.Thread(target=dummy_worker)
        self.manager.register_task("task2", thread2)
        self.assertEqual(self.manager.get_status_summary(), "2 tasks running")

    def test_get_status_summary_with_names(self):
        """get_status_summary includes task names when requested."""

        def dummy_worker():
            pass

        # One task with name
        thread1 = threading.Thread(target=dummy_worker)
        self.manager.register_task("download_data", thread1)
        summary = self.manager.get_status_summary(include_names=True)
        self.assertEqual(summary, "1 task running: download_data")

        # Multiple tasks with names
        thread2 = threading.Thread(target=dummy_worker)
        self.manager.register_task("process_file", thread2)
        summary = self.manager.get_status_summary(include_names=True)
        self.assertIn("2 tasks running:", summary)
        self.assertIn("download_data", summary)
        self.assertIn("process_file", summary)

    def test_get_status_summary_truncates_long_names(self):
        """get_status_summary truncates long task names."""

        def dummy_worker():
            pass

        thread = threading.Thread(target=dummy_worker)
        long_name = "a" * 30
        self.manager.register_task(long_name, thread)
        summary = self.manager.get_status_summary(include_names=True)

        # Name should be truncated to 15 chars + "..."
        self.assertIn("aaaaaaaaaaaaaaa...", summary)

    def test_get_status_summary_limits_displayed_tasks(self):
        """get_status_summary limits the number of displayed task names."""

        def dummy_worker():
            pass

        # Register 5 tasks
        for i in range(5):
            thread = threading.Thread(target=dummy_worker)
            self.manager.register_task("task{}".format(i), thread)

        summary = self.manager.get_status_summary(include_names=True)
        self.assertIn("5 tasks running:", summary)
        # Should show first 3 tasks plus "..."
        self.assertIn("task0", summary)
        self.assertIn("task1", summary)
        self.assertIn("task2", summary)
        self.assertIn("...", summary)

    def test_wait_for_all_tasks_waits_for_completion(self):
        """wait_for_all_tasks blocks until threads complete."""
        results = []

        def worker():
            time.sleep(0.05)
            results.append("done")

        thread = threading.Thread(target=worker)
        self.manager.register_task("task", thread)
        thread.start()

        # Results should be empty before waiting
        self.assertEqual(len(results), 0)

        self.manager.wait_for_all_tasks()

        # Results should be populated after waiting
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], "done")

    def test_mark_completed_triggers_ui_invalidate_callback(self):
        """Completing a task invalidates the UI when callback is configured."""

        callback = unittest.mock.MagicMock()
        self.manager.set_ui_invalidate_callback(callback)
        thread = threading.Thread(target=lambda: None)
        task_id = self.manager.register_task("task", thread)

        self.manager.mark_completed(task_id)

        callback.assert_called_once()

    def test_mark_failed_triggers_ui_invalidate_callback(self):
        """Failing a task invalidates the UI when callback is configured."""

        callback = unittest.mock.MagicMock()
        self.manager.set_ui_invalidate_callback(callback)
        thread = threading.Thread(target=lambda: None)
        task_id = self.manager.register_task("task", thread)

        self.manager.mark_failed(task_id, RuntimeError("boom"))

        callback.assert_called_once()

    def test_enqueue_output_triggers_ui_invalidate_callback(self):
        """Enqueuing output invalidates the UI when callback is configured."""

        callback = unittest.mock.MagicMock()
        self.manager.set_ui_invalidate_callback(callback)

        self.manager.enqueue_output("task_0", "hello")

        callback.assert_called_once()

    def test_get_queued_output_handles_empty_race(self):
        """Queue empty races are handled gracefully."""

        class RaceQueue(object):
            def empty(self):
                return False

            def get_nowait(self):
                raise queue.Empty

        original_queue = self.manager._output_queue
        self.manager._output_queue = RaceQueue()
        try:
            self.assertEqual(self.manager.get_queued_output(), [])
        finally:
            self.manager._output_queue = original_queue


if __name__ == "__main__":
    unittest.main()
