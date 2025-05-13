from langchain_core.messages import HumanMessage, SystemMessage
from bs4 import BeautifulSoup, Comment
import re
import json
from urllib.parse import urljoin
import subprocess

def clean_html_for_llm(url):
    html_content = subprocess.check_output(["curl", "-s", url])
    soup = BeautifulSoup(html_content, "html.parser")
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    for element in soup.find_all(['script', 'style', 'noscript', 'iframe', 'svg', 'canvas']):
        element.extract()
    for element in soup.find_all(style=True):
        if any(pattern in element.get('style').lower() for pattern in ["display:none", "display: none", "visibility:hidden", "visibility: hidden"]):
            element.extract()
    for element in soup.find_all(class_=True):
        classes = element.get('class')
        if any(cls in str(classes).lower() for cls in ["hidden", "d-none", "hide", "invisible", "visually-hidden"]):
            element.extract()
    if soup.head:
        for tag in soup.head.find_all(['meta', 'link']):
            tag.extract()
    content_str = str(soup.body) if soup.body else str(soup)
    content_str = re.sub(r'\n\s*\n', '\n', content_str)
    content_str = re.sub(r'^\s+|\s+$', '', content_str, flags=re.MULTILINE)
    content_str = re.sub(r' {2,}', ' ', content_str)
    content_str = re.sub(r' data-[^=]*="[^"]*"', '', content_str)
    content_str = re.sub(r' class="[^"]*"', '', content_str)
    content_str = re.sub(r' id="[^"]*"', '', content_str)
    content_str = re.sub(r' style="[^"]*"', '', content_str)
    for _ in range(3):
        content_str = re.sub(r'<([a-z0-9]+)>\s*</\1>', '', content_str, flags=re.IGNORECASE)
    return content_str

def extract_pure_json(text: str) -> list[dict]:
    """Extract JSON content from text that might be wrapped in markdown code blocks."""
    json_pattern = r"```(?:json)?\s*([\s\S]*?)```|```(?:json)?\s*([\s\S]*)"
    match = re.search(json_pattern, text)
    if match:
        json_text = (match.group(1) or match.group(2)).strip()
        return json.loads(json_text)
    return json.loads(text.strip())

def is_json_complete(text: str) -> bool:
    try:
        json.loads(text)
        return True
    except json.JSONDecodeError:
        return False
    
def extract_links_from_page(html_content, base_url):
    """Extract all links from a page with their text"""
    soup = BeautifulSoup(html_content, 'html.parser')
    links = []
    
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        if href.startswith('#') or href.startswith('javascript:'):
            continue
            
        text = link.text.strip()
        full_url = urljoin(base_url, href)
        links.append({"url": full_url, "text": text})
    
    return links

def get_repertoire_links(links, model):
    links_text = "\n".join([f"{i+1}. {link['text']} - {link['url']}" for i, link in enumerate(links[:30])])
    prompt = f"""
    Which of these links is most likely to lead to a page with the theater's repertoire/program/schedule of performances?
    Respond with JSON in this format:
    [
        {{
            "url": "https://example.com/link",
            "confidence": 0.9  // A score between 0-1 indicating confidence this link leads to repertoire
        }}
    ]
    
    Only include links with confidence > 0.5. Sort by confidence descending.    
    """
    human_message = f"""
    Available links on the page:
    {links_text}
    """
    messages = [
        SystemMessage(prompt),
        HumanMessage(human_message)
    ]
    response = model.invoke(messages)
    try:
        response_content = response.content
        response_json = extract_pure_json(response_content)
        return response_json
    except Exception as e:
        print(f"Error parsing LLM response: {e}")
        return []

def identify_page_and_get_repertoire_links(page_text, links, model):
    """
    Ask the LLM to identify if this is a repertoire page and/or suggest links to repertoire pages
    """
    links_text = "\n".join([f"{i+1}. {link['text']} - {link['url']}" for i, link in enumerate(links[:30])])
    prompt = f"""
    Analyze theater website page and determine:

    1. Is this a repertoire/program page that lists upcoming performances? (Yes/No)
    2. If this is NOT a repertoire page, which of these links is most likely to lead to a page with the theater's repertoire/program/schedule of performances?

    Respond with JSON in this format:
    {{
        "is_repertoire_page": true/false,
        "recommended_links": [
            {{
                "url": "https://example.com/link",
                "confidence": 0.9  // A score between 0-1 indicating confidence this link leads to repertoire
            }}
        ]
    }}
    
    Only include links with confidence > 0.5. Sort by confidence descending.
    """
    human_message = f"""
    Page content excerpt:
    {page_text}

    Available links on the page:
    {links_text}
    """
    messages = [
        SystemMessage(prompt),
        HumanMessage(human_message)
    ]
    response = model.invoke(messages)
    try:
        response_content = response.content
        json_match = re.search(r'({[\s\S]*})', response_content)
        if json_match:
            response_json = json.loads(json_match.group(1))
        else:
            response_json = json.loads(response_content)
        return response_json
    except Exception as e:
        print(f"Error parsing LLM response: {e}")
        return {
            "is_repertoire_page": False,
            "recommended_links": []
        }