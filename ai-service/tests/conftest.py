import os
import tempfile

import pytest
from jose import jwt

os.environ.setdefault("JWT_SECRET", "test-secret-for-ci-only")

from app.core.config import get_settings  # noqa: E402


@pytest.fixture
def settings():
    get_settings.cache_clear()
    return get_settings()


@pytest.fixture
def auth_headers(settings):
    token = jwt.encode({"sub": "sri", "roles": ["CANDIDATE"]}, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def tmp_vector_store_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d
