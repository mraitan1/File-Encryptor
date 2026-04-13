import argparse
from getpass import getpass

from src.EncryptClient import process_file


def main():
    parser = argparse.ArgumentParser(description="File Encryptor / Decryptor")
    parser.add_argument(
        "mode",
        choices = ["encrypt", "decrypt"],
        help = "Whether to encrypt or decrypt the file"
    )
    parser.add_argument(
        "input_path",
        help = "Path to the input file"
    )
    parser.add_argument(
        "-o", "--output",
        dest = "output_path",
        help = "Optional output file path (default: input.ext + .enc/.dec)"
    )
    parser.add_argument(
        "--delete",
        action = "store_true",
        help = "Delete original after verifying encrypted file can be decrypted."
    )

    args = parser.parse_args()

    password = getpass("Enter password: ")
    confirm = None

    if args.mode == "encrypt":
        confirm = getpass("Confirm password: ")
        if password != confirm:
            print("Passwords do not match. Aborting.")
            return

    try:
        out = process_file(
            mode = args.mode,
            input_path = args.input_path,
            password = password,
            output_path = args.output_path,
            delete_original = args.delete
        )
        print(f"Success! Output written to: {out}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
