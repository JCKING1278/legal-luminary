import os
import re
from langsmith import Client

def find_potential_contacts(text):
    """Find potential contacts in the text."""
    contacts = []
    # Regex for a phone number
    phone_regex = re.compile(r'\(\d{3}\)\s*\d{3}-\d{4}')
    # Regex for a URL, simple version
    url_regex = re.compile(r'https?://[^\s\)]+')
    # Regex for a name (markdown link)
    name_regex = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

    # Split the text into lines and check each line
    for line in text.splitlines():
        phone_match = phone_regex.search(line)
        url_match = url_regex.search(line)
        name_match = name_regex.search(line)

        if phone_match and url_match and name_match:
            # Heuristic: if the name in the markdown link is part of the URL, it's likely what we want
            name_from_link = name_match.group(1)
            url_from_link = name_match.group(2)
            
            # A simple check to see if the name is plausible
            if len(name_from_link) > 3:
                 contacts.append({
                    "name": name_from_link,
                    "url": url_from_link,
                    "phone": phone_match.group(0)
                })

    return contacts

def main():
    """
    Finds potential contacts in markdown files and adds them to a LangSmith dataset.
    """
    client = Client()
    dataset_name = "Contact names"

    # Ensure the dataset exists
    try:
        dataset = client.read_dataset(dataset_name=dataset_name)
    except Exception:
        dataset = client.create_dataset(dataset_name=dataset_name, description="Potential contact names found on the website.")

    # Find all markdown files
    markdown_files = []
    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".md"):
                markdown_files.append(os.path.join(root, file))

    # Process each file
    for file_path in markdown_files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            contacts = find_potential_contacts(content)
            
            for contact in contacts:
                try:
                    # Check if an example with the same output already exists
                    examples = client.list_examples(dataset_id=dataset.id, data_outputs=contact)
                    if not list(examples):
                        client.create_example(
                            inputs={"file_path": file_path},
                            outputs=contact,
                            dataset_id=dataset.id,
                        )
                        print(f"Added '{contact['name']}' from '{file_path}' to dataset '{dataset_name}'.")
                    else:
                        print(f"Example for '{contact['name']}' from '{file_path}' already exists.")
                except Exception as e:
                    print(f"Error adding example: {e}")

if __name__ == "__main__":
    main()
