# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""A helper for collecting stats on carried out actions

"""

__docformat__ = 'restructuredtext'

# TODO: we have already smth in progressbar...  check
import humanize
from ..utils import auto_repr

_COUNTS = (
    'files', 'urls',
    'add_git', 'add_annex',
    'skipped', 'overwritten', 'renamed',
    'downloaded', 'downloaded_size', 'downloaded_time'
)
_LISTS = (
    'merges',
)
_FORMATTERS = {
    # TODO:
    'downloaded_size' : humanize.naturalsize,
    'merges': lambda merges: ", ".join('->'.join(merge) for merge in merges)
}

# @auto_repr
class ActivityStats(object):
    """Helper to collect/pass statistics on carried out actions

    It also keeps track of total counts, which do not get reset by
    reset() call, and "total" stat could be obtained by .get_total()
    Could be done so many other ways
    """
    __metrics__ = _COUNTS + _LISTS
    __slots__ = __metrics__ + ('_current', '_total')

    def __init__(self, **vals):
        self._current = {}
        self._total = {}
        self.reset(full=True, vals=vals)

    def __repr__(self):
        # since auto_repr doesn't support "non-0" values atm
        return "%s(%s)" % (self.__class__.__name__,
                           ", ".join(["%s=%s" % (k,v) for k, v in self._current.items() if v]))

    # Comparisons operate solely on _current
    def __eq__(self, other):
        return (self._current == other._current)# and (self._total == other._total)

    def __ne__(self, other):
        return (self._current != other._current)# or (self._total != other._total)

    def __iadd__(self, other):
        for m in other.__metrics__:
            # not inplace for increased paranoia for bloody lists, and dummy implementation of *add
            self._current[m] = self._current[m] + other._current[m]
            self._total[m] = self._total[m] + other._total[m]
        return self

    def __add__(self, other):
        # crashed
        # out = deepcopy(self)
        # so doing ugly way
        out = ActivityStats(**self._current)
        out._total = self._total.copy()
        out += other
        return out

    def __setattr__(self, key, value):
        if key in self.__metrics__:
            self._current[key] = value
        else:
            return super(ActivityStats, self).__setattr__(key, value)

    def __getattribute__(self, key):
        if (not key.startswith('_')) and key in self.__metrics__:
            return self._current[key]
        else:
            return super(ActivityStats, self).__getattribute__(key)

    def _get_updated_total(self):
        """Return _total updated with _current
        """
        out = self._total.copy()
        for k, v in self._current.items():
            # not inplace + so we could create copies of lists
            out[k] = out[k] + v
        return out

    def increment(self, k):
        """Helper for incrementing counters"""
        self._current[k] += 1

    def _reset_values(self, d, vals={}):
        for c in _COUNTS:
            d[c] = vals.get(c, 0)
        for l in _LISTS:
            d[l] = vals.get(l, [])

    def reset(self, full=False, vals={}):
        # Initialize
        if not full:
            self._total = self._get_updated_total()
        self._reset_values(self._current, vals=vals)
        if full:
            self._reset_values(self._total, vals=vals)

    def get_total(self):
        """Return a copy of total stats (for convenience)"""
        return self.__class__(**self._get_updated_total())

    def as_dict(self):
        return self._current.copy()

    def as_str(self, mode='full'):
        """

        Parameters
        ----------
        mode : {'full', 'line'}
        """

        # Example
        """
URLs processed: {urls}
 downloaded: {downloaded}
 downloaded size: {downloaded_size}
Files processed: {files}
 skipped: {skipped}
 renamed: {renamed}
 added to git: {add_git}
 added to annex: {add_annex}
 overwritten: {overwritten}
Branches merged:
  upstream -> master
"""

        # TODO: improve
        entries = self.as_dict()
        entries.update({
            k: (_FORMATTERS[k](entries[k]) if entries[k] else '')
            for k in _FORMATTERS
        })

        out_formats = [
            ("URLs processed", "urls"),
            (" downloaded", "downloaded"),
            (" size", "downloaded_size"),
            ("Files processed", "files"),
            (" skipped", "skipped"),
            (" renamed", "renamed"),
            (" overwritten", "overwritten"),
            (" +git",  "add_git"),
            (" +annex", "add_annex"),
            ("Branches merged", "merges")
        ]
        # Filter out empty/0 ones
        out = ["%s: " % s + str(entries[m]) for s, m in out_formats if entries[m]]
        if mode == 'full':
            return '\n'.join(out)
        elif mode == 'line':
            for i in range(len(out)):
                if out[i][0] != ' ':
                    out[i] = '  ' + out[i]
            return ','.join(out).lstrip()
            return "{files} files (git/annex: {add_git}/{add_annex}), " \
                   "{skipped} skipped, {renamed} renamed, {overwritten} overwritten".format(
                    **entries)
        else:
            raise ValueError("Unknown mode %s" % mode)
