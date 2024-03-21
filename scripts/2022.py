import json
import os
import sys
import zipfile


def parse_line_to_dict(line):
    record_type = line[0:2]
    record_data = {
        "00": lambda l: {
            "Record Type": "Vorlaufrecord",
            "Kanton": l[2:4],
            "SSL Nummer": l[4:19].strip(),
            "Erstellungsdatum": l[19:27],
            "Textzeile 1": l[27:67].strip(),
            "Textzeile 2": l[67:107].strip(),
            "Code Status": l[107:110].strip()
        },
        "06": lambda l: {
            "Record Type": "Progressive Quellensteuertarife",
            "Transaktionsart": l[2:4],
            "Kanton": l[4:6],
            "QSt-Code": l[6:16].strip(),
            "Datum gültig ab": l[16:24],
            "Steuerbares Einkommen ab": l[24:33].strip(),
            "Tarifschritt in Fr.": l[33:42].strip(),
            "Code Geschlecht": l[42:43].strip(),
            "Anzahl Kinder": l[43:45].strip(),
            "Mindeststeuer in Fr.": l[45:54].strip(),
            "Steuer %-Satz": l[54:59].strip(),
            "Code Status": l[59:62].strip()
        },
        "11": lambda l: {
            "Record Type": "Vordefinierte Kategorien",
            "Transaktionsart": l[2:4],
            "Kanton": l[4:6],
            "Code Steuerart": l[6:16].strip(),
            "Datum gültig ab": l[16:24],
            "Steuerbares Einkommen ab": l[24:33].strip(),
            "Tarifschritt in Fr.": l[33:42].strip(),
            "Code Geschlecht": l[42:43].strip(),
            "Anzahl Kinder": l[43:45].strip(),
            "Mindeststeuer in Fr.": l[45:54].strip(),
            "Steuer %-Satz": l[54:59].strip(),
            "Code Status": l[59:62].strip()
        },
        "12": lambda l: {
            "Record Type": "Bezugsprovision",
            "Transaktionsart": l[2:4],
            "Kanton": l[4:6],
            "Code Bezugsprovision": l[6:16].strip(),
            "Datum gültig ab": l[16:24],
            "Steuerbares Einkommen ab": l[24:33].strip(),
            "Tarifschritt in Fr.": l[33:42].strip(),
            "Code Geschlecht": l[42:43].strip(),
            "Anzahl Kinder": l[43:45].strip(),
            "Mindeststeuer in Fr.": l[45:54].strip(),
            "Steuer %-Satz": l[54:59].strip(),
            "Code Status": l[59:62].strip()
        },
        "13": lambda l: {
            "Record Type": "Medianwert",
            "Transaktionsart": l[2:4],
            "Kanton": l[4:6],
            "Code Medianwert": l[6:16].strip(),
            "Datum gültig ab": l[16:24],
            "Steuerbares Einkommen ab": l[24:33].strip(),
            "Tarifschritt in Fr.": l[33:42].strip(),
            "Code Geschlecht": l[42:43].strip(),
            "Anzahl Kinder": l[43:45].strip(),
            "Mindeststeuer in Fr.": l[45:54].strip(),
            "Steuer %-Satz": l[54:59].strip(),
            "Code Status": l[59:62].strip()
        },
        "99": lambda l: {
            "Record Type": "Endrecord",
            "Absender SSL": l[2:17].strip(),
            "Absender Kanton": l[17:19],
            "Anzahl übermittelter Records": l[19:27],
            "Checksumme Betrag": l[27:36].strip(),
            "Code Status": l[36:39].strip()
        }
    }.get(record_type, lambda l: {"Error": "Unknown record type"})(line)

    return record_data


def file_to_json_structure(filepath):
    envelope = {"header": None, "content": [], "footer": None}
    with open(filepath, 'r') as file:
        for line in file:
            parsed_line = parse_line_to_dict(line)
            if parsed_line["Record Type"] == "Vorlaufrecord":
                envelope["header"] = parsed_line
            elif parsed_line["Record Type"] == "Endrecord":
                envelope["footer"] = parsed_line
            else:
                envelope["content"].append(parsed_line)
    return envelope


def main():
    # Check if a workspace parameter is provided
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <workspace_directory> <year>")
        sys.exit(1)

    # The workspace directory is the first argument
    workspace_dir = sys.argv[1]
    year = int(sys.argv[2])

    # Define the directory containing the zip file and the output directory
    zip_dir = os.path.join(workspace_dir, "downloads")
    output_dir = os.path.join(zip_dir, "unzipped_files")
    source_dir = os.path.join(workspace_dir, "src")

    # Define the zip file name
    zip_file = "tarife.zip"

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Unzip the files to the output directory
    with zipfile.ZipFile(os.path.join(zip_dir, zip_file), 'r') as zip_ref:
        zip_ref.extractall(output_dir)

    # Change to the output directory
    os.chdir(output_dir)

    all_files_data = []
    # Display the contents of all extracted files
    for file in os.listdir('.'):
        json_structure = file_to_json_structure(file)
        all_files_data.append(json_structure)

    combined_json_filename = f"{year}.json"
    combined_json_filepath = os.path.join(source_dir, combined_json_filename)  # Save in source_dir
    # Write all files' JSON data to a single file in the source_dir
    with open(combined_json_filepath, 'w') as combined_json_file:
        json.dump(all_files_data, combined_json_file, indent=2)


if __name__ == "__main__":
    main()
