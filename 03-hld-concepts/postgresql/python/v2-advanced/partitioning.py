class PostgresPartitioner:
    def get_partition(self, date_str: str) -> str:
        return f"part_{date_str[:7].replace('-', '_')}"
