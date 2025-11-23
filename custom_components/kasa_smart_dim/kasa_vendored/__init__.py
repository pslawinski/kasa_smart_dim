"""Python interface for TP-Link's smart home devices.

All common, shared functionalities are available through `SmartDevice` class::

    x = SmartDevice("192.168.1.1")
    print(x.sys_info)

For device type specific actions `SmartBulb`, `SmartPlug`, or `SmartStrip`
 should be used instead.

Module-specific errors are raised as `SmartDeviceException` and are expected
to be handled by the user of the library.
"""

from importlib.metadata import version
from warnings import warn

from .credentials import Credentials
from .deviceconfig import (
    DeviceConfig,
    DeviceFamilyType,
    EncryptType,
)
from .discover import Discover
from .emeterstatus import EmeterStatus
from .exceptions import (
    AuthenticationException,
    SmartDeviceException,
    TimeoutException,
    UnsupportedDeviceException,
)
from .iotprotocol import (
    IotProtocol,
    _deprecated_TPLinkSmartHomeProtocol,  # noqa: F401
)
from .protocol import BaseProtocol
from .smartbulb import SmartBulb, SmartBulbPreset, TurnOnBehavior, TurnOnBehaviors
from .smartdevice import DeviceType, SmartDevice
from .smartdimmer import SmartDimmer
from .smartlightstrip import SmartLightStrip
from .smartplug import SmartPlug
from .smartprotocol import SmartProtocol
from .smartstrip import SmartStrip

try:
    __version__ = version("python-kasa")
except Exception:
    __version__ = "unknown"


__all__ = [
    "Discover",
    "BaseProtocol",
    "IotProtocol",
    "SmartProtocol",
    "SmartBulb",
    "SmartBulbPreset",
    "TurnOnBehaviors",
    "TurnOnBehavior",
    "DeviceType",
    "EmeterStatus",
    "SmartDevice",
    "SmartDeviceException",
    "SmartPlug",
    "SmartStrip",
    "SmartDimmer",
    "SmartLightStrip",
    "AuthenticationException",
    "UnsupportedDeviceException",
    "TimeoutException",
    "Credentials",
    "DeviceConfig",
    "EncryptType",
    "DeviceFamilyType",
]

deprecated_names = ["TPLinkSmartHomeProtocol"]


def __getattr__(name):
    if name in deprecated_names:
        warn(f"{name} is deprecated", DeprecationWarning, stacklevel=1)
        return globals()[f"_deprecated_{name}"]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
