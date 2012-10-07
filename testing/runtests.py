# -*- coding: utf-8 -*-

import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

from django.core.management import call_command

if __name__ == "__main__":
    args = sys.argv[1:]
    call_command("test", *args, verbosity=2)
