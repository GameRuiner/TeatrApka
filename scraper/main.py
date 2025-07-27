import getpass
import os
from langchain_together import ChatTogether
from dotenv import load_dotenv
from urllib.parse import urlparse
from agent import clean_html_for_llm_async, extract_links_from_page, get_repertoire_links
from geminy_agent import parse_repertoires_from_page
from google import genai
import json
import asyncio

load_dotenv();

if not os.environ.get("TOGETHER_API_KEY"):
    os.environ["TOGETHER_API_KEY"] = getpass.getpass("Enter API key for Together AI: ")

model = ChatTogether(model="Qwen/Qwen2.5-Coder-32B-Instruct")

client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

def get_theatre_name(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    if domain.startswith("www."):
        domain = domain[4:]
    main_part = domain.rsplit('.', 1)[0]
    return main_part

theatres = [
    "https://teatrdramatyczny.pl/", 
    "https://www.teatr2strefa.pl", 
    "https://teatrstudio.pl", 
    "https://teatrpolski.waw.pl/", 
    "https://www.wspolczesny.pl/",
    "https://nowyteatr.org/pl",
    "https://www.teatrpolonia.pl",
    "https://teatr6pietro.pl",
    "https://garnizonsztuki.org.pl",
    "https://teatr-rampa.pl",
    "https://teatrwarsawy.pl",
    "https://potemotem.com/"
    ]

theatres = ["https://teatrdramatyczny.pl/"]

for theatre_url in theatres:
    theater_name = get_theatre_name(theatre_url)
    print(f"Parsing theatre {theater_name}, url {theatre_url}")
    
    content = asyncio.run(clean_html_for_llm_async(theatre_url))
    links = extract_links_from_page(content, theatre_url)
    repertoire_links = get_repertoire_links(links, model)

    for url_obj in repertoire_links:
        url = url_obj["url"]
        print(f"Repertoire link {url}")
        content = asyncio.run(clean_html_for_llm_async(url))
        performances = parse_repertoires_from_page(content, client)
        print(f"Found {len(performances)} performances")
        json_path = f"../theatre_project/json_data/{theater_name}.json"
        if performances:
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as file:
                    existing_data = json.load(file)
            else:
                existing_data = {
                    "name": theater_name,
                    "address": "",
                }

            existing_data["performances"] = performances

            with open(json_path, "w", encoding="utf-8") as file:
                json.dump(existing_data, file, ensure_ascii=False, indent=2)