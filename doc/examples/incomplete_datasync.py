from snorky.services.datasync import DataSyncService, DataSyncBackend

datasync = DataSyncService("datasync", [
    # dealer list (will be explained in the next chapter)
])
datasync_backend = DataSyncBackend("datasync_backend", datasync)
