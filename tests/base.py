import unittest

from app import create_app
from app.db import ensure_database_ready
from app.extensions import db


class DevBrainTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
        )
        self.ctx = self.app.app_context()
        self.ctx.push()
        ensure_database_ready()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()
