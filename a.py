from bs4 import BeautifulSoup
import re
import os
import html

def extract_html_info(html):
    # Parse the HTML content
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract the title text
    title = soup.title.string if soup.title else None
    
    # Extract the author from the meta tag
    author = None
    author_meta = soup.find('meta', attrs={'name': 'author'})
    if author_meta:
        author = author_meta.get('content')
    
    # Extract the body HTML
    body = str(soup.body) if soup.body else None
    
    return title, author, body

def process_body_html(body_html):
    supported_tags = {
    "a", "abbr", "acronym", "address", "article", "aside", "audio", "b", "bdi", "bdo", "big",
    "blockquote", "body", "br", "caption", "cite", "code", "data", "dd", "del", "details", "dfn",
    "div", "dl", "dt", "em", "figcaption", "figure", "footer", "font", "h1", "h2", "h3", "h4",
    "h5", "h6", "header", "hr", "i", "iframe", "img", "ins", "kbd", "li", "main", "mark", "nav",
    "noscript", "ol", "p", "pre", "q", "rp", "rt", "ruby", "s", "samp", "section", "small", "span",
    "strike", "strong", "sub", "sup", "summary", "svg", "table", "tbody", "td", "template", "tfoot",
    "th", "thead", "time", "tr", "tt", "u", "ul", "var", "video", "math", "mrow", "msup", "msub",
    "mover", "munder", "msubsup", "moverunder", "mfrac", "mlongdiv", "msqrt", "mroot", "mi", "mn", "mo"
}
    soup = BeautifulSoup(body_html, 'html.parser')

    # Check if there is an <h1> tag in the document
    has_h1 = soup.find('h1') is not None

    # Decrease heading levels and remove id attributes
    for heading in soup.find_all(re.compile('^h[1-6]$')):
        if has_h1:
            current_level = int(heading.name[1])
            new_level = min(current_level + 1, 6)  # Ensure the level doesn't go beyond h6
            heading.name = f'h{new_level}'
        if 'id' in heading.attrs:
            del heading['id']

    # Replace <br> tags with newline characters
    for br in soup.find_all('br'):
        br.insert_before('\n')
        br.unwrap()

    # Replace <p> tags with newline characters (before and after the content)
    for p in soup.find_all('p'):
        p.insert_before('\n')
        p.insert_after('\n')

    # Remove unwanted tags but keep <b>, <big>, <small>, <br>, and <h2> to <h6>
    for tag in soup.find_all():
        if tag.name not in supported_tags:
            tag.unwrap()

    # Get the text and remove extra whitespace
    text = str(soup)
    text = re.sub(r'\n\s*\n', '\n', text)  # Remove consecutive newlines
    text = text.replace("<br/>", "\n")
    text = text.replace("\n\n\n", "\n\n")
    text = text.strip()  # Remove leading and trailing whitespace

    return text

def main(book_file):
    with open(book_file, "r", encoding = "utf-8") as file:
        html_content = file.read()
    title, author, body = extract_html_info(html_content)
    processed_text = process_body_html(body).splitlines()
    autpoot_text = [f"<h1>{title}</h1>", author] + [line for line in processed_text if line != "<!DOCTYPE html>" and not line.startswith("את הטקסט לעיל ") and not line.startswith("https://benyehud") and line != title]
    join_lines = html.unescape("\n".join(autpoot_text))
    with open(book_file, "w", encoding = "utf-8") as autpoot:
        autpoot.write(join_lines)
    #os.remove(book_file)


books_folder = "html"
for root, dir, file in os.walk(books_folder):
    for file_name in file:
        if file_name.lower().endswith(".html"):
            file_path = os.path.join(root, file_name)
            main(file_path)
 
