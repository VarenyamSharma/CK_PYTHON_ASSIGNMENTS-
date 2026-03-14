import os
import hashlib
import shutil

# Function to calculate SHA256 checksum
def get_checksum(file_path):
    sha256 = hashlib.sha256()

    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(4096):
                sha256.update(chunk)
    except:
        return None

    return sha256.hexdigest()


def find_duplicates(directory, min_size):
    checksums = {}
    duplicates = {}

    for root, dirs, files in os.walk(directory):
        for file in files:
            path = os.path.join(root, file)

            # Skip small files
            if os.path.getsize(path) < min_size:
                continue

            checksum = get_checksum(path)

            if checksum in checksums:
                duplicates.setdefault(checksum, []).append(path)
            else:
                checksums[checksum] = path

    return checksums, duplicates


def generate_report(duplicates):
    with open("duplicate_report.txt", "w") as report:
        for checksum, files in duplicates.items():
            report.write(f"\nChecksum: {checksum}\n")
            for file in files:
                report.write(file + "\n")

    print("Report saved as duplicate_report.txt")


def handle_duplicates(checksums, duplicates):
    if not duplicates:
        print("No duplicate files found.")
        return

    print("\nDuplicate files found:\n")

    for checksum, files in duplicates.items():
        print(f"\nChecksum: {checksum}")
        print("Original:", checksums[checksum])

        for i, file in enumerate(files):
            print(f"{i}: {file}")

    choice = input("\nEnter 'd' to delete duplicates, 'm' to move them, or 'n' to ignore: ")

    if choice == "d":
        for files in duplicates.values():
            for file in files:
                os.remove(file)
                print(f"Deleted: {file}")

    elif choice == "m":
        move_dir = input("Enter directory to move duplicates: ")
        os.makedirs(move_dir, exist_ok=True)

        for files in duplicates.values():
            for file in files:
                shutil.move(file, move_dir)
                print(f"Moved: {file}")


def main():
    directory = input("Enter directory to scan: ")

    size_mb = float(input("Enter minimum file size (MB) to check duplicates: "))
    min_size = size_mb * 1024 * 1024

    checksums, duplicates = find_duplicates(directory, min_size)

    generate_report(duplicates)

    handle_duplicates(checksums, duplicates)


if __name__ == "__main__":
    main()