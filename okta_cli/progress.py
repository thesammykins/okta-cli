"""
Progress indicators and loading utilities for long-running operations.
"""

import click
import time
import threading
from typing import Optional, Callable, Any
from contextlib import contextmanager


class ProgressIndicator:
    """
    Progress indicator for long-running operations.
    """

    def __init__(
        self,
        message: str = "Processing...",
        show_percent: bool = True,
        show_eta: bool = True,
    ):
        """
        Initialize progress indicator.

        Args:
            message: Progress message
            show_percent: Whether to show percentage
            show_eta: Whether to show estimated time
        """
        self.message = message
        self.show_percent = show_percent
        self.show_eta = show_eta
        self._running = False
        self._thread = None

    def start(self):
        """Start the progress indicator."""
        self._running = True
        self._thread = threading.Thread(target=self._spinner)
        self._thread.daemon = True
        self._thread.start()

    def stop(self):
        """Stop the progress indicator."""
        self._running = False
        if self._thread:
            self._thread.join()

    def _spinner(self):
        """Spinner animation."""
        chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        i = 0
        while self._running:
            char = chars[i % len(chars)]
            click.echo(f"\r{char} {self.message}", nl=False)
            time.sleep(0.1)
            i += 1
        click.echo("\r" + " " * (len(self.message) + 2) + "\r", nl=False)


@contextmanager
def progress_spinner(message: str = "Processing..."):
    """
    Context manager for spinner progress indicator.

    Args:
        message: Progress message

    Example:
        with progress_spinner("Connecting to API..."):
            # Long running operation
            time.sleep(2)
    """
    indicator = ProgressIndicator(message)
    indicator.start()
    try:
        yield
    finally:
        indicator.stop()


def progress_bar(
    iterable,
    label: str = "Processing",
    show_percent: bool = True,
    show_eta: bool = True,
):
    """
    Create a progress bar for iterables.

    Args:
        iterable: Iterable to process
        label: Progress label
        show_percent: Show percentage
        show_eta: Show estimated time

    Returns:
        Progress bar iterator
    """
    return click.progressbar(
        iterable,
        label=label,
        show_percent=show_percent,
        show_eta=show_eta,
        item_show_func=lambda x: str(x) if x else "",
    )


def timed_progress_bar(
    duration: float, label: str = "Processing", steps: int = 100
) -> None:
    """
    Create a timed progress bar.

    Args:
        duration: Duration in seconds
        label: Progress label
        steps: Number of steps
    """
    step_duration = duration / steps

    with click.progressbar(
        range(steps), label=label, show_percent=True, show_eta=True
    ) as bar:
        for _ in bar:
            time.sleep(step_duration)


def api_call_with_progress(
    func: Callable, *args, message: str = "Making API call...", **kwargs
) -> Any:
    """
    Execute API call with progress indicator.

    Args:
        func: Function to call
        *args: Function arguments
        message: Progress message
        **kwargs: Function keyword arguments

    Returns:
        Function result
    """
    with progress_spinner(message):
        return func(*args, **kwargs)


def connectivity_test_progress(
    test_func: Callable, message: str = "Testing connectivity"
) -> Any:
    """
    Execute connectivity test with progress animation.

    Args:
        test_func: Function to test connectivity
        message: Progress message

    Returns:
        Test result
    """
    with click.progressbar(
        range(100), label=message, show_percent=True, show_eta=True
    ) as bar:
        # Simulate network delay
        for i in range(50):
            time.sleep(0.01)
            bar.update(1)

        # Execute test
        result = test_func()

        # Complete progress
        for i in range(50):
            time.sleep(0.01)
            bar.update(1)

        return result


def batch_operation_progress(
    items: list, operation: Callable, label: str = "Processing items"
) -> list:
    """
    Execute batch operation with progress bar.

    Args:
        items: List of items to process
        operation: Operation to perform on each item
        label: Progress label

    Returns:
        List of results
    """
    results = []

    with click.progressbar(items, label=label, show_percent=True, show_eta=True) as bar:
        for item in bar:
            result = operation(item)
            results.append(result)

    return results


def multi_step_progress(steps: list, step_names: list = None) -> Any:
    """
    Execute multi-step operation with progress tracking.

    Args:
        steps: List of functions to execute
        step_names: Optional names for each step

    Returns:
        Last step result
    """
    if step_names is None:
        step_names = [f"Step {i+1}" for i in range(len(steps))]

    result = None

    with click.progressbar(
        range(len(steps)),
        label="Multi-step operation",
        show_percent=True,
        show_eta=True,
    ) as bar:
        for i, step in enumerate(steps):
            bar.label = step_names[i]
            result = step()
            bar.update(1)

    return result


class StepProgress:
    """
    Step-by-step progress indicator.
    """

    def __init__(self, total_steps: int, title: str = "Progress"):
        """
        Initialize step progress.

        Args:
            total_steps: Total number of steps
            title: Progress title
        """
        self.total_steps = total_steps
        self.current_step = 0
        self.title = title
        self.steps = []

    def add_step(self, name: str, description: str = ""):
        """
        Add a step to the progress.

        Args:
            name: Step name
            description: Step description
        """
        self.steps.append(
            {"name": name, "description": description, "completed": False}
        )

    def start_step(self, step_index: int = None):
        """
        Start a specific step.

        Args:
            step_index: Step index (uses current_step if None)
        """
        if step_index is None:
            step_index = self.current_step

        if step_index < len(self.steps):
            step = self.steps[step_index]
            click.echo(f"[{step_index + 1}/{self.total_steps}] {step['name']}")
            if step["description"]:
                click.echo(f"   {step['description']}")

    def complete_step(self, step_index: int = None):
        """
        Complete a specific step.

        Args:
            step_index: Step index (uses current_step if None)
        """
        if step_index is None:
            step_index = self.current_step

        if step_index < len(self.steps):
            self.steps[step_index]["completed"] = True
            click.echo(click.style(f"   ✅ Completed", fg="green"))
            self.current_step += 1

    def fail_step(self, step_index: int = None, error: str = ""):
        """
        Mark a step as failed.

        Args:
            step_index: Step index (uses current_step if None)
            error: Error message
        """
        if step_index is None:
            step_index = self.current_step

        if step_index < len(self.steps):
            click.echo(click.style(f"   ❌ Failed: {error}", fg="red"))

    def show_summary(self):
        """Show progress summary."""
        completed = sum(1 for step in self.steps if step["completed"])
        click.echo(f"\n{self.title} Summary:")
        click.echo(f"Completed: {completed}/{self.total_steps}")

        for i, step in enumerate(self.steps):
            status = "✅" if step["completed"] else "❌"
            click.echo(f"  {status} {step['name']}")


def create_progress_callback(total: int, label: str = "Processing"):
    """
    Create a progress callback function.

    Args:
        total: Total number of items
        label: Progress label

    Returns:
        Progress callback function
    """
    bar = click.progressbar(range(total), label=label, show_percent=True, show_eta=True)
    bar.__enter__()

    def callback(completed: int):
        bar.update(completed - bar.pos)

    def finish():
        bar.__exit__(None, None, None)

    callback.finish = finish
    return callback


# Convenient decorators
def with_progress(message: str = "Processing..."):
    """
    Decorator to add progress spinner to functions.

    Args:
        message: Progress message
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            with progress_spinner(message):
                return func(*args, **kwargs)

        return wrapper

    return decorator


def with_progress_bar(message: str = "Processing..."):
    """
    Decorator to add progress bar to functions that return iterables.

    Args:
        message: Progress message
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if hasattr(result, "__iter__"):
                return progress_bar(result, message)
            return result

        return wrapper

    return decorator
