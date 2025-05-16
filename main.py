import getpass
import os
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from urllib.parse import urlparse
from agent import clean_html_for_llm, extract_links_from_page, get_repertoire_links
from geminy_agent import parse_repertoires_from_page
from google import genai
import json

load_dotenv();

if not os.environ.get("TOGETHER_API_KEY"):
    os.environ["TOGETHER_API_KEY"] = getpass.getpass("Enter API key for Together AI: ")

model = init_chat_model("Qwen/Qwen2.5-Coder-32B-Instruct", model_provider="together")

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
    "https://teatr6pietro.pl"
    ]
theatres = ["https://garnizonsztuki.org.pl"]

for theatre_url in theatres:
    theater_name = get_theatre_name(theatre_url)
    print(f"Parsing theatre {theater_name}, url {theatre_url}")
    content = clean_html_for_llm(theatre_url)
    links = extract_links_from_page(content, theatre_url)
    repertoire_links = get_repertoire_links(links, model)

    for url_obj in repertoire_links:
        url = url_obj["url"]
        print(f"Repertoire link {url}")
        content = clean_html_for_llm(url)
        performances = parse_repertoires_from_page(content, client)
        print(f"Found {len(performances)} performances")
        if len(performances) > 0:
            with open(f"temp/{theater_name}.json", "w") as file:
                json.dump(performances, file, ensure_ascii=False, indent=2)
            break       

    # if len(repertoire_links) > 0:
    #     first_url = repertoire_links[0]
    #     if first_url["confidence"] >= 0.7:
    #         url = first_url['url']
    #     else:
    #         url = theatre_url