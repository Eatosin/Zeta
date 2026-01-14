# API Reference

## Endpoints

### `POST /generate`
Generates a test suite from requirements text.
*   **Body:** `{"requirements_text": "string"}`
*   **Response:** JSON Test Suite with Z-Score Risk Analysis.

### `POST /codegen`
Converts a JSON test plan into executable Selenium Python code.
*   **Body:** `{"test_plan": {Obj}}`
*   **Response:** Python script string.
