"""Bounded stable ordinary-file reads and streaming tool hashes for offline identity inputs. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: ordinary — line 42
# parameter: maximum — line 42
# parameter: path — line 42
# variable: path — line 44
# variable: item — line 45
# variable: before — line 47
# variable: descriptor — line 50
# variable: stream — line 57
# variable: first — line 58
# variable: after — line 67
# definition: read_source — line 76
# parameter: maximum — line 76
# parameter: path — line 76
# variable: stream — line 79
# variable: value — line 80
# definition: file_hash — line 88
# parameter: maximum — line 88
# parameter: path — line 88
# variable: stream — line 91
# variable: digest — line 92
# variable: total — line 92
# variable: chunk — line 93
# variable: total — line 94
# END CODE MAP

from __future__ import annotations

import hashlib
import os
import stat
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import BinaryIO

from .desktop_io import Rejected


@contextmanager
def ordinary(path: Path, maximum: int) -> Iterator[BinaryIO]:
    """Open one nonblocking regular one-link descriptor and reject changed identity/bytes before returning success."""
    path = path.absolute()
    if any(item.is_symlink() or item.is_junction() for item in (path, *path.parents)):
        raise Rejected("linked_input")
    before = path.stat()
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size > maximum:
        raise Rejected("input_file_or_bound")
    descriptor = os.open(
        path,
        os.O_RDONLY
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_NONBLOCK", 0)
        | getattr(os, "O_BINARY", 0),
    )
    with os.fdopen(descriptor, "rb") as stream:
        first = os.fstat(stream.fileno())
        if (
            not stat.S_ISREG(first.st_mode)
            or first.st_nlink != 1
            or (first.st_dev, first.st_ino) != (before.st_dev, before.st_ino)
            or first.st_size > maximum
        ):
            raise Rejected("input_changed")
        yield stream
        after = os.fstat(stream.fileno())
        if (first.st_size, first.st_mtime_ns, first.st_ctime_ns) != (
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        ):
            raise Rejected("input_changed")


def read_source(path: Path, maximum: int) -> bytes:
    """Read a finite ordinary input without FIFO blocking, linked aliases or unbounded allocation."""
    try:
        with ordinary(path, maximum) as stream:
            value = stream.read(maximum + 1)
        if len(value) > maximum:
            raise Rejected("input_bound")
        return value
    except OSError:
        raise Rejected("input_unavailable") from None


def file_hash(path: Path, maximum: int) -> str:
    """Stream a finite pinned executable/resource without raising small evidence-file limits or duplicating its bytes."""
    try:
        with ordinary(path, maximum) as stream:
            digest, total = hashlib.sha256(), 0
            while chunk := stream.read(min(1024 * 1024, maximum + 1 - total)):
                total += len(chunk)
                if total > maximum:
                    raise Rejected("input_bound")
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        raise Rejected("input_unavailable") from None
