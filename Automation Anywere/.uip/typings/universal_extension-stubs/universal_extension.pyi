from universal_extension import ExtensionResult

from .types import DynamicChoiceCommandWorkSpaceType
from .types import DynamicChoiceCommandBotType
from .types import DynamicChoiceCommandBotsList
from .types import ExtensionFields
from .types import UipNls


class UniversalExtension(object):
    uip: UipNls

    def bots_list(self, fields: DynamicChoiceCommandBotsList) -> ExtensionResult:
        ...

    def extension_start(self, fields: ExtensionFields) -> ExtensionResult:
        ...

    ...
