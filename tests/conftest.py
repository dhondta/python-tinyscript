# -*- coding: UTF-8 -*-
import pytest

from utils import remove


@pytest.fixture(scope="session", autouse=True)
def clear_files_teardown():
    yield None
    for f in [".test-script.py", ".tinyscript-test.ini", "report.pdf", "test-script.py"]:
        remove(f)

