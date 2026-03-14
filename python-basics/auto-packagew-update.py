import subprocess
import logging

# Configure logging
logging.basicConfig(
    filename="package_update.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Function to check available updates
def check_updates():
    print("\nChecking for available updates...\n")

    try:
        result = subprocess.run(
            ["apt", "list", "--upgradable"],
            capture_output=True,
            text=True
        )

        packages = result.stdout.split("\n")[1:]  # skip header
        packages = [p for p in packages if p.strip() != ""]

        if not packages:
            print("No updates available.")
            return []

        print("Available Updates:\n")

        for i, pkg in enumerate(packages):
            print(f"{i}. {pkg}")

        return packages

    except Exception as e:
        logging.error(f"Error checking updates: {e}")
        print("Error while checking updates.")
        return []


# Function to update all packages
def update_all():
    print("\nUpdating all packages...\n")

    try:
        subprocess.run(["sudo", "apt", "update"])
        subprocess.run(["sudo", "apt", "upgrade", "-y"])

        print("All packages updated successfully.")
        logging.info("All packages updated successfully")

    except Exception as e:
        logging.error(f"Failed to update packages: {e}")
        print("ERROR: Failed to update packages.")


# Function to update a specific package
def update_specific(package_name):
    print(f"\nUpdating package: {package_name}\n")

    try:
        subprocess.run(["sudo", "apt", "install", package_name, "-y"])

        print(f"{package_name} updated successfully.")
        logging.info(f"{package_name} updated successfully")

    except Exception as e:
        logging.error(f"Failed to update {package_name}: {e}")
        print(f"ERROR: Failed to update {package_name}")


# Main program
packages = check_updates()

if packages:
    choice = input("\nEnter 'all' to update all packages OR enter package index number: ")

    if choice.lower() == "all":
        update_all()

    else:
        try:
            index = int(choice)
            package_name = packages[index].split("/")[0]
            update_specific(package_name)

        except:
            print("Invalid input.")