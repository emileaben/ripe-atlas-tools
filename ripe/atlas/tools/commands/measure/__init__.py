from __future__ import print_function, absolute_import

import sys

from ...exceptions import RipeAtlasToolsException
from ..base import Factory as BaseFactory
from .ping import PingMeasureCommand
from .traceroute import TracerouteMeasureCommand
from .dns import DnsMeasureCommand
from .sslcert import SslcertMeasureCommand
from .http import HttpMeasureCommand
from .ntp import NtpMeasureCommand


class Factory(BaseFactory):

    TYPES = {
        "ping": PingMeasureCommand,
        "traceroute": TracerouteMeasureCommand,
        "dns": DnsMeasureCommand,
        "sslcert": SslcertMeasureCommand,
        "http": HttpMeasureCommand,
        "ntp": NtpMeasureCommand,
    }

    def __init__(self):

        self.build_class = None
        if len(sys.argv) >= 2:
            self.build_class = self.TYPES.get(sys.argv[1].lower())

        if not self.build_class:
            raise RipeAtlasToolsException(
                "The measurement type you requested is invalid.  Please choose "
                "one of {}.".format(", ".join(self.TYPES.keys()))
            )

    def create(self, *args, **kwargs):
        return self.build_class(*args, **kwargs)
