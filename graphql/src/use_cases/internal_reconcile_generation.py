from src.use_cases.adapter_interfaces.storage import StorageInternalReconcileGenerationInterface


class InternalReconcileGeneration:
    def __init__(self, storage: StorageInternalReconcileGenerationInterface):
        self.storage = storage
