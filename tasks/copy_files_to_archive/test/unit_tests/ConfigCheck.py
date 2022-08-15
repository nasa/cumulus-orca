class ConfigCheck:
    multipart_chunksize = None

    def __init__(self, multipart_chunksize):
        self.multipart_chunksize = multipart_chunksize

    bad_config = None

    def check_multipart_chunksize(
        self, copy_source, destination_bucket, destination_key, ExtraArgs, Config
    ):
        try:
            if Config.multipart_chunksize != self.multipart_chunksize:
                self.bad_config = Config
        except Exception as ex:
            bad_config = ex
