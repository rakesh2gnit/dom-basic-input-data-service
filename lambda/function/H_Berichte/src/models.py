from dataclasses import dataclass

@dataclass
class Report:
    report_file_name: str
    report_key: str
    created_timestamp: str
    updated_timestamp: str
    data: list
    status: str