# -*- coding: utf-8 -*-
"""
Monkey's patched methods for the SpooledTemporaryFile class.
This is because the SpooledTemporaryFile does not inherit / implement the IOBase class.
"""
from tempfile import SpooledTemporaryFile


def _readable(self):
    return self._file.readable()


def _writable(self):
    return self._file.writable()


def _seekable(self):
    return self._file.seekable()


SpooledTemporaryFile.readable = _readable
SpooledTemporaryFile.writable = _writable
SpooledTemporaryFile.seekable = _seekable
