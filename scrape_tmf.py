import requests
from bs4 import BeautifulSoup
import json

# URL of the TMF projects page
url = "https://tmf.cio.gov/projects/"

# Send a GET request to fetch the page content
response = requests.get(url)

# Parse the page content with BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Find the starting point for active investments
start = soup.find('h1', id='active-investments-1').find_next_sibling()

# Collect all projects into a list
projects = []
current_tag = start

while current_tag and current_tag.name != 'h1':  # Assuming there is an h1 tag marking the end or next major section
    if current_tag.name == 'h2':  # Assuming each project starts with an h2 tag
        project = {'Title': current_tag.text.strip()}
        content_tag = current_tag.find_next_sibling()

        include_project = True  # Flag to determine if the project should be included

        while content_tag and content_tag.name not in ['h2', 'h1']:  # Continue until the next project's h2 or the end h1
            if content_tag.name == 'p':
                text = content_tag.text.strip()
                if ':' in text:
                    key, value = text.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    if any(x in key.lower() for x in ["commission", "agency", "department", "corps", "forces"]):
                        project['Agency'] = key
                        project['Project'] = value
                    else:
                        project[key] = value
            elif content_tag.name == 'div' and 'project-details' in content_tag.get('class', []):
                details = {}
                for p in content_tag.find_all('p'):
                    if ':' in p.text:
                        detail_key, detail_value = p.text.split(':', 1)
                        detail_key = detail_key.strip()
                        detail_value = detail_value.strip()
                        if detail_key == "Commercial product" and detail_value.lower() == "yes":
                            include_project = False  # Exclude project if Commercial product is yes
                        details[detail_key] = detail_value
                project['Project Details'] = details
            elif content_tag.name == 'ul':
                project['More Details'] = [li.text.strip() for li in content_tag.find_all('li')]

            content_tag = content_tag.find_next_sibling()

        if include_project:
            projects.append(project)

    current_tag = current_tag.find_next_sibling()

# Save to JSON file
with open('tmf_projects.json', 'w', encoding='utf-8') as outfile:
    json.dump(projects, outfile, indent=4, ensure_ascii=False)

print("Filtered project data has been saved to 'tmf_projects.json'")
