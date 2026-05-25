# -*- coding: utf-8 -*-

from . import models
from . import report


def post_init_hook(env):
    """
    Check for external dependencies and warn if missing (though Odoo checks external_dependencies too).
    Validate that l10n_ec is installed and configured.
    """
    pass


def uninstall_hook(env):
    """
    Warn about legal implications of removing signature history.
    """
    pass
