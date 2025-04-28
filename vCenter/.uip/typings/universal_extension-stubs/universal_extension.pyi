from universal_extension import ExtensionResult

from .types import DynamicChoiceCommandFunction
from .types import DynamicChoiceCommandDataCenter
from .types import DynamicChoiceCommandEsxHost
from .types import DynamicChoiceCommandVmList
from .types import ExtensionFields
from .types import UipNls


class UniversalExtension(object):
    uip: UipNls

    def list_datacenter(self, fields: DynamicChoiceCommandDataCenter) -> ExtensionResult:
        ...

    def list_esx(self, fields: DynamicChoiceCommandEsxHost) -> ExtensionResult:
        ...

    def list_vm(self, fields: DynamicChoiceCommandVmList) -> ExtensionResult:
        ...

    def extension_start(self, fields: ExtensionFields) -> ExtensionResult:
        ...

    ...
