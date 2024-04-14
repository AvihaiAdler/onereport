import csv
from io import SEEK_SET
import logging
import sys
import json


def read(reader: csv.DictReader, /) -> list[dict[str, str]]:
    return [{key: value for key, value in row.items()} for row in reader]


def read_csv(path: str) -> list[dict[str, str]]:
    try:
        with open(path, encoding="utf-8-sig", mode="r", newline="") as csv_file:
            dialect = csv.Sniffer().sniff(csv_file.read())
            csv_file.seek(0, SEEK_SET)

            return read(csv.DictReader(csv_file, dialect=dialect))
    except OSError as os_err:
        logging.error(f"failed to open '{path}'\nreason: {os_err.strerror}")


def parse_platoon(platoon: str, /) -> str:
    for c in platoon:
        if c.isdigit():
            return f"_{c}"

    return "UNCATEGORIZED"


def to_json(dct: dict[str, str], company: str, /) -> dict[str, str]:
    return {
        "id": dct["id"],
        "first_name": dct["first_name"],
        "last_name": dct["last_name"],
        "company": company,
        "platoon": parse_platoon(dct["platoon"]),
    }


def parse(parsed_csv: list[dict[str, str]], company: str, /) -> dict:
    return {"Personnel": [to_json(personnel, company) for personnel in parsed_csv]}


def main() -> None:
    argv = sys.argv
    if len(argv) < 3:
        logging.error(f"Usage: {sys.argv[0]} <path/to/csv/file> <company_letter>")
        exit(1)

    csv_path = sys.argv[1]
    parsed = parse(read_csv(csv_path), sys.argv[2])

    with open(f"{csv_path}.json", mode="w", encoding="utf-8") as fp:
        json.dump(parsed, fp, ensure_ascii=False)


if __name__ == "__main__":
    main()
