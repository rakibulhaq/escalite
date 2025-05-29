class QueryBuilder:

    @classmethod
    def set_config(cls
                   , config: dict):
        cls.config = config

    @classmethod
    def prepare_time_range(cls):
        db_type = cls.config
