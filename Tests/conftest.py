"""pytest configuration of the library tests (python3 -m pytest Tests).

``test_instrument.py`` is the interactive tool for real instruments, not a test module:
pytest must not import it.
"""

collect_ignore = ["test_instrument.py"]
