from agent import extract_pure_json

def parse_repertoires_from_page(html_content: str, client) -> list[dict]:
    """Parse the given HTML and return a JSON list of repertoire items found on the page."""
    system_message = """
        I will provide you with an HTML snippet containing information about theater performances. Extract all performances, including their titles, dates, and times, and return the result as a JSON array with the following format:
        ```
        [
        {
            "title": "Performance name",
            "date": "YYYY-MM-DD",
            "time": "HH:MM",
            "status": "Performance status",
            "place": "Performance place",
        }
        ]
        ```
        Important rules:
        - Return ONLY valid JSON (no extra text or markdown).
        - If you are reaching the token limit or need to stop, DO NOT cut off in the middle of a JSON object. 
        Finish the current object fully and stop after a comma (`,`) or after the closing bracket (`]`) if at the end.
        - When continuing later, start exactly where you left off, starting with the next JSON object or the closing bracket.
    """
    messages = F"""
        {system_message}

        {html_content}
    """
    response = client.models.generate_content(
         model="gemini-2.0-flash", contents=messages
    )
    pure_json = extract_pure_json(response.text)
    return pure_json