from jinja2 import Template
from typing import Dict, Any
from loguru import logger
import black # For auto-formatting

class SeleniumGenerator:
    """
    Generates production-grade Selenium (Python) scripts using Page Object Model (POM).
    Uses Jinja2 templates for safe code generation.
    """

    # SOTA Template: Page Object Model + Pytest
    TEST_TEMPLATE = """
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- PAGE OBJECT MODEL ---
class GeneratedPage:
    def __init__(self, driver):
        self.driver = driver
        self.url = "{{ url }}"

    def load(self):
        self.driver.get(self.url)

    {% for action in actions %}
    def {{ action.func_name }}(self, value=None):
        # Action: {{ action.description }}
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.{{ action.selector_type }}, "{{ action.selector }}"))
        )
        {% if action.type == 'click' %}
        element.click()
        {% elif action.type == 'input' %}
        element.clear()
        element.send_keys(value)
        {% endif %}
    {% endfor %}

# --- TEST CASES ---
@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless") 
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

def test_generated_scenario(driver):
    page = GeneratedPage(driver)
    page.load()
    
    {% for step in steps %}
    # Step: {{ step.description }}
    page.{{ step.func_name }}({{ step.value if step.value else '' }})
    {% endfor %}
    
    # Assertions would go here
    assert driver.title != "" 
"""

    def generate_test_script(self, test_plan: Dict[str, Any]) -> str:
        """
        Compiles a test plan dictionary into executable Python code.
        """
        logger.info("Generating Selenium Script...")
        
        try:
            template = Template(self.TEST_TEMPLATE)
            
            # Render code
            raw_code = template.render(
                url=test_plan.get("url", "https://example.com"),
                actions=test_plan.get("actions", []),
                steps=test_plan.get("steps", [])
            )
            
            # Format code using Black (Industry Standard)
            formatted_code = black.format_str(raw_code, mode=black.Mode())
            return formatted_code
            
        except Exception as e:
            logger.error(f"Code Generation Failed: {e}")
            raise e

    def save_script(self, code: str, filename: str = "generated_test.py"):
        """Saves the code to disk."""
        with open(filename, "w") as f:
            f.write(code)
        logger.info(f" Test Script Saved: {filename}")
