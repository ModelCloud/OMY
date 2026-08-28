# Copyright 2025 The OMY team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""LogBar-backed tqdm-compatible progress bar.

This module replaces the ``tqdm`` dependency with a thin wrapper around
``LogBar`` (https://pypi.org/project/LogBar) so that existing ``tqdm`` call
sites continue to work without pulling ``tqdm`` as a direct dependency of OMY.
"""

import sys
import time
from collections.abc import Iterable, Iterator
from contextlib import contextmanager, suppress
from types import TracebackType
from typing import Any

from logbar import LogBar


class tqdm:
    """Drop-in-ish progress bar backed by LogBar."""

    _lock: Any = None

    def __init__(
        self,
        iterable: Iterable[Any] | None = None,
        desc: str | None = None,
        total: int | None = None,
        leave: bool = True,
        file: Any = None,
        ncols: int | None = None,
        mininterval: float = 0.1,
        maxinterval: float = 10.0,
        miniters: int | None = None,
        ascii: bool | None = None,
        disable: bool = False,
        unit: str = "it",
        unit_scale: bool | float = False,
        dynamic_ncols: bool = False,
        smoothing: float = 0.3,
        bar_format: str | None = None,
        initial: int = 0,
        position: int | None = None,
        postfix: dict[str, Any] | None = None,
        unit_divisor: int = 1000,
        write_bytes: bool | None = None,
        lock_args: Any = None,
        nrows: int | None = None,
        colour: str | None = None,
        delay: float = 0,
        gui: bool = False,
        **kwargs: Any,
    ):
        self.iterable = iterable
        self.desc = desc or ""
        self.total = total
        self.n = initial
        self.initial = initial
        self.disable = disable
        self.unit = unit
        self.leave = leave
        self.file = file
        self._closed = False
        self._bar: Any = None
        self._start = time.time()

        if total is None and iterable is not None and hasattr(iterable, "__len__"):
            try:
                self.total = len(iterable)
            except Exception:
                self.total = None

        if not disable:
            with suppress(Exception):
                if iterable is not None:
                    self._bar = LogBar.shared().pb(iterable)
                elif total is not None:
                    self._bar = LogBar.shared().pb(total)
                else:
                    # Unknown total; use an empty iterable to let update() drive progress.
                    self._bar = LogBar.shared().pb(())

                if self._bar is not None:
                    if self.desc:
                        self._bar.title(self.desc)
                    if initial:
                        self._bar.current_iter_step = initial
                        self._bar.draw()

    def __iter__(self) -> Iterator[Any]:
        if self.disable or self._bar is None:
            if self.iterable is None:
                raise TypeError("'tqdm' object is not iterable")
            for obj in self.iterable:
                self.n += 1
                yield obj
            return

        if self.iterable is None:
            raise TypeError("'tqdm' object is not iterable")

        for obj in self._bar:
            self.n = self._bar.current_iter_step
            yield obj

    def update(self, n: int = 1) -> None:
        if self.disable or n is None:
            return
        if n == 0:
            return
        self.n += n
        if self._bar is not None:
            self._bar.current_iter_step = self.n
            with suppress(Exception):
                self._bar.draw()

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._bar is not None:
            with suppress(Exception):
                self._bar.close()

    def __enter__(self) -> "tqdm":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def __del__(self) -> None:
        self.close()

    def set_description(self, desc: str | None = None, refresh: bool = True) -> None:
        self.desc = desc or ""
        if self._bar is not None and self.desc:
            with suppress(Exception):
                self._bar.title(self.desc)
                if refresh:
                    self._bar.draw()

    def set_postfix(self, ordered_dict: Any = None, refresh: bool = True, **kwargs: Any) -> None:
        # LogBar does not have a direct postfix field; map to subtitle.
        postfix = ordered_dict or kwargs
        if postfix:
            subtitle = ", ".join(f"{k}={v}" for k, v in postfix.items())
            if self._bar is not None:
                with suppress(Exception):
                    self._bar.subtitle(subtitle)
                    if refresh:
                        self._bar.draw()

    @property
    def format_dict(self) -> dict[str, Any]:
        elapsed = max(0.0, time.time() - self._start)
        rate = (self.n - self.initial) / elapsed if elapsed > 0 else 0
        return {
            "n": self.n,
            "total": self.total,
            "elapsed": elapsed,
            "rate": rate,
        }

    @classmethod
    def set_lock(cls, lock: Any) -> None:
        cls._lock = lock

    @classmethod
    def get_lock(cls) -> Any:
        return cls._lock

    @classmethod
    def write(
        cls,
        s: str,
        file: Any = None,
        end: str = "\n",
        nolock: bool = False,
    ) -> None:
        file = file or sys.stdout
        file.write(s + end)
        with suppress(Exception):
            file.flush()


def trange(*args: Any, **kwargs: Any) -> tqdm:
    """LogBar-backed ``tqdm(range(...))`` shorthand."""
    return tqdm(range(*args), **kwargs)


@contextmanager
def logging_redirect_tqdm(loggers: Any = None, tqdm_class: type = tqdm):
    """No-op context manager kept for tqdm API compatibility.

    LogBar does not need log redirection to avoid clobbering terminal output,
    so this simply yields.
    """
    yield
