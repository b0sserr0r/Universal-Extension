from universal_extension import ExtensionResult

from .types import DynamicChoiceCommandFunction
from .types import DynamicChoiceCommandJobList
from .types import ExtensionFields
from .types import UipNls


class UniversalExtension(object):
    uip: UipNls

    def job_list(self, fields: DynamicChoiceCommandJobList) -> ExtensionResult:
        ...

    def extension_start(self, fields: ExtensionFields) -> ExtensionResult:
        ...

    ...
