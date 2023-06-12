class DictionaryHandler:
    def filter_keys(self, dictionary: dict, key_filter: callable):
        return {key: value for key, value in dictionary.items() if key_filter(key)}

    def filter_values(self, dictionary: dict, value_filter: callable):
        return {key: value for key, value in dictionary.items() if value_filter(value)}

    def parse_values(self, dictionary: dict, value_parser: callable):
        return {key: value_parser(value) for key, value in dictionary.items()}
