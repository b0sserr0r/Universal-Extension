from universal_extension import ExtensionResult

from .types import ExtensionFields
from .types import UipNls


class UniversalExtension(object):
    uip: UipNls

    def extension_start(self, fields: ExtensionFields) -> ExtensionResult:
        ...

    ...
