import os
import unittest
from unittest.mock import patch


os.environ.setdefault("BOT_TOKEN", "123456:TEST_TOKEN")
os.environ.setdefault("TELEGRAM_API_ID", "123456")
os.environ.setdefault("TELEGRAM_API_HASH", "0" * 32)
os.environ.setdefault("AUTHORIZED_USER_ID", "123456789")

import main


class MainStartupTests(unittest.TestCase):
    def test_build_application_registers_lifecycle_callbacks(self):
        with patch.object(main.Application, "builder") as builder_factory:
            builder = builder_factory.return_value
            builder.token.return_value = builder
            builder.post_init.return_value = builder
            builder.post_shutdown.return_value = builder

            app = object()
            builder.build.return_value = app

            result = main.build_application("token")

        self.assertIs(result, app)
        builder.token.assert_called_once_with("token")
        builder.post_init.assert_called_once_with(main.post_init)
        builder.post_shutdown.assert_called_once_with(main.post_shutdown)
        builder.build.assert_called_once_with()

    def test_module_entrypoint_delegates_to_run(self):
        self.assertTrue(hasattr(main, "run"))


if __name__ == "__main__":
    unittest.main()
