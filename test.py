from googlesearch import search
import requests
from bs4 import BeautifulSoup

# Perform the search
query = "How the weeknd became famous"
results = list(search(query, num_results=3))

# Function to extract plain text from a webpage
def get_plain_text(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        # Get text
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        text = '\n'.join(line for line in lines if line)
        return text
    except Exception as e:
        return f"Failed to retrieve {url}: {str(e)}"

# Get plain text from top 3 pages
for url in results:
    print(f"Text from {url}:\n")
    print(get_plain_text(url))
    print("\n" + "="*80 + "\n")
