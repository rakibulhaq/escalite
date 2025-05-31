from escalite.formatters.base_formatter import Formatter


class DictTableFormatter(Formatter):
    def format(self, data: dict) -> str:
        if not data:
            return ""
        key_width = max(len(str(k)) for k in data.keys())
        val_width = max(len(str(v)) for v in data.values())
        lines = [
            f"{'Key'.ljust(key_width)} | {'Value'.ljust(val_width)}",
            f"{'-' * key_width}-+-{'-' * val_width}"
        ]
        for k, v in data.items():
            lines.append(f"{str(k).ljust(key_width)} | {str(v).ljust(val_width)}")
        return "\n".join(lines)
