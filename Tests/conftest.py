# Copyright (C) 2025-2026 Erik Medeossi
# This file is part of Open Lab Automation.
# Licensed under the GNU General Public License v3.0; see the LICENSE file.

"""pytest configuration of the library tests (python3 -m pytest Tests).

``test_instrument.py`` is the interactive tool for real instruments, not a test module:
pytest must not import it.
"""

collect_ignore = ["test_instrument.py"]
