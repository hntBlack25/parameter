import re
import requests
from bs4 import BeautifulSoup
import logging
from jinja2 import Template

# إعداد تسجيل الأحداث
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# قالب HTML لعرض المعلمات
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Extracted Parameters</title>
    <style>
        .important { color: red; }
        .normal { color: blue; }
        .dangerous { color: green; }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <h1>Extracted Parameters</h1>
    <h2>  Support me please</h2>
    <h3>   Black25 *https://t.me/Black2_5*</h3>
    <table>
        <thead>
            <tr>
                <th>Tag</th>
                <th>Attribute</th>
                <th>Value</th>
                <th>Importance</th>
            </tr>
        </thead>
        <tbody>
            {% for param in parameters %}
            <tr class="{{ 'dangerous' if param.is_dangerous else 'important' if param.is_important else 'normal' }}">
                <td>{{ param.tag }}</td>
                <td>{{ param.attribute }}</td>
                <td>{{ param.value }}</td>
                <td>{{ 'Dangerous' if param.is_dangerous else 'Important' if param.is_important else 'Normal' }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    <h2>Thank you for using my tools, bye :)</h2>
</body>
</html>
"""

def fetch_page_content(url):
    """Fetches the HTML content of the given URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve the page: {e}")
        return None

def extract_attributes(element):
    """Extracts all attributes of an HTML element."""
    attributes = {attr: value for attr, value in element.attrs.items()}
    return attributes

def determine_importance(attributes):
    """Determines if a parameter is important based on its attributes."""
    important_attributes = ['name', 'id', 'class']
    return any(attr in important_attributes for attr in attributes)

def determine_danger(attributes, text):
    """Determines if a parameter is dangerous based on its attributes or text content."""
    dangerous_keywords = ['password', 'token', 'secret', 'api_key', 'credit_card', 'ssn', 'iban', 'private']
    # Check attributes
    attr_check = any(dangerous_keyword in attributes.get('name', '').lower() or 
                    dangerous_keyword in attributes.get('type', '').lower() 
                    for dangerous_keyword in dangerous_keywords)
    # Check text content
    text_check = any(dangerous_keyword in text.lower() for dangerous_keyword in dangerous_keywords)
    return attr_check or text_check

def extract_parameters(soup, tags):
    """Extracts detailed parameter information for the given tags."""
    parameters = []
    for tag in tags:
        for element in soup.find_all(tag):
            attributes = extract_attributes(element)
            text_content = element.get_text().strip()
            for attr, value in attributes.items():
                param_info = {
                    'tag': tag,
                    'attribute': attr,
                    'value': value,
                    'is_important': determine_importance(attributes),
                    'is_dangerous': determine_danger(attributes, text_content)
                }
                parameters.append(param_info)
            # Include text content as a parameter if it's significant
            if text_content:
                param_info = {
                    'tag': tag,
                    'attribute': 'text_content',
                    'value': text_content,
                    'is_important': False,
                    'is_dangerous': determine_danger({}, text_content)
                }
                parameters.append(param_info)
    return parameters

def get_all_parameters(url):
    """Extracts all form parameters and their details from a webpage."""
    content = fetch_page_content(url)
    if not content:
        return []
    
    soup = BeautifulSoup(content, 'html.parser')

    tags = ['input', 'select', 'textarea', 'button', 'form', 'fieldset', 'legend', 'label', 'datalist', 'output', 'option']

    all_params = extract_parameters(soup, tags)
    
    return all_params

def generate_html(parameters, filename='output.html'):
    """Generates an HTML file with the parameters displayed."""
    template = Template(html_template)
    rendered_html = template.render(parameters=parameters)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(rendered_html)
    logging.info(f"HTML report generated: {filename}")

if __name__ == "__main__":
    url = "https://moe.gov.ly/"  # ضع رابط الموقع الذي تريد فحصه هنا
    parameters = get_all_parameters(url)
    generate_html(parameters)
    print("[+]HTML report generated successfully!")
    print("[+]You can send me a telegram message if there is any error or correction. Good luck:)")
    print("^Telegram^ [+] https://t.me/Black2_5")
