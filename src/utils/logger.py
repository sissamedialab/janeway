"""
Janeway logging utilities and main logger
"""

import logging
from contextvars import ContextVar

context_logprefix = ContextVar("prefix", default="")

# ContextVar(..., default=[]) should be safe, but it looks like a risky habit /
# confusing situation. I prefer dealing explicitly with LookupErrors
context_logparts = ContextVar("parts")


class LogPrefix(object):
    """A logging prefix scoped for the current thread"""

    @property
    def rendered_prefix(self):
        return context_logprefix.get()

    @rendered_prefix.setter
    def rendered_prefix(self, val):
        context_logprefix.set(val)

    @property
    def _parts(self):
        try:
            return context_logparts.get()
        except LookupError:
            context_logparts.set([])
        return context_logparts.get()

    def push(self, item):
        self._parts.append(str(item))
        self.update()

    def pop(self):
        self._parts.pop()
        self.update()

    def update(self):
        self.rendered_prefix = ":".join(self._parts)

    def set(self, *parts):
        context_logparts.set(list(parts))
        self.update()

    def do_prefix(self, msg):
        if _prefix.rendered_prefix:
            return "[%s] %s" % (self.rendered_prefix, msg)
        else:
            return msg


_prefix = LogPrefix()


class PrefixedLoggerAdapter(logging.LoggerAdapter):
    """Adds the current prefix to the log line"""

    def process(self, msg, extra):
        return _prefix.do_prefix(msg), extra

    def push_prefix(self, item):
        _prefix.push(item)

    def pop_prefix(self):
        _prefix.pop()

    def set_prefix(self, *values):
        _prefix.set(*values)


def get_logger(logger_name, extra=None):
    logger = logging.getLogger(logger_name)
    return PrefixedLoggerAdapter(logger, extra or {})
