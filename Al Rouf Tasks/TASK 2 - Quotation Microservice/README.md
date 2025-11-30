````markdown
## usage.md: Quotation Service API Usage Guide 📝

This document provides instructions for setting up and interacting with the **Quotation Service** FastAPI application.

---

## 🚀 Getting Started

The Quotation Service is a simple FastAPI application that calculates total prices for a list of items (applying a margin percentage to the unit cost) and generates a draft quotation email in both English and Arabic.

### Prerequisites

1.  **Python 3.7+**
2.  **FastAPI** and **Uvicorn**:
    ```bash
    pip install fastapi "uvicorn[standard]" pydantic
    ```

### Running the Server

Assuming your file is named `main.py`, you can run the service using Uvicorn:

```bash
uvicorn main:app --reload
````

The service will be available at `http://127.0.0.1:8000`.

-----

## 🩺 API Endpoints

### 1\. Root/Ping Endpoint

Use this endpoint to confirm the service is running.

  * **URL:** `/`
  * **Method:** `GET`
  * **Response Status:** `200 OK`
  * **Example Response:**
    ```json
    {
      "status": "ok",
      "message": "Quotation Service is running."
    }
    ```

-----

### 2\. Generate Quote Endpoint

This is the main endpoint used to calculate the quote totals and generate the email draft.

  * **URL:** `/quote`
  * **Method:** `POST`
  * **Content-Type:** `application/json`

#### 📥 Request Body Schema (`QuoteRequest`)

The request body is a JSON object that must conform to the following structure:

| Field | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| **`client`** | `Client` object | Details of the client. | Yes |
| **`currency`** | `string` | The currency code (e.g., "USD", "SAR"). | Yes |
| **`items`** | `array` of `Item` objects | List of items for the quote. | Yes |
| **`delivery_terms`** | `string` | Terms of delivery (e.g., "FOB Jeddah", "Ex Works"). | Yes |
| **`notes`** | `string` | Optional general notes for the quote. | No |

**`Client` Object:**

| Field | Type | Description | Default |
| :--- | :--- | :--- | :--- |
| **`name`** | `string` | Client's name. | N/A |
| **`contact`** | `string` | Contact details (e.g., email or phone). | N/A |
| **`lang`** | `string` | Preferred language ("en" or "ar"). | "en" |

**`Item` Object:**

| Field | Type | Description | Default |
| :--- | :--- | :--- | :--- |
| **`sku`** | `string` | Stock Keeping Unit or item identifier. | N/A |
| **`qty`** | `integer` | Quantity requested. | N/A |
| **`unit_cost`** | `number` | The cost of one unit *to you*. | N/A |
| **`margin_pct`** | `number` | The desired profit margin percentage. | N/A |

#### 📤 Example Request

```json
{
  "client": {
    "name": "Acme Corp",
    "contact": "contact@acme.com",
    "lang": "en"
  },
  "currency": "USD",
  "items": [
    {
      "sku": "PRD-001",
      "qty": 5,
      "unit_cost": 500.00,
      "margin_pct": 20.0
    },
    {
      "sku": "SRV-CONSULT",
      "qty": 1,
      "unit_cost": 2500.00,
      "margin_pct": 15.0
    }
  ],
  "delivery_terms": "3-5 business days after payment confirmation",
  "notes": "Special discount applied to PRD-001 unit cost."
}
```

#### ✅ Example Response

The response includes the final calculations for each line item, the grand total, and the generated email drafts.

```json
{
  "currency": "USD",
  "line_items": [
    {
      "sku": "PRD-001",
      "qty": 5,
      "unit_cost": 500.0,
      "margin_pct": 20.0,
      "selling_price_per_unit": 600.0,
      "line_total": 3000.0
    },
    {
      "sku": "SRV-CONSULT",
      "qty": 1,
      "unit_cost": 2500.0,
      "margin_pct": 15.0,
      "selling_price_per_unit": 2875.0,
      "line_total": 2875.0
    }
  ],
  "grand_total": 5875.0,
  "email_draft": {
    "en": "Dear Acme Corp,\n\nThank you for your inquiry. Please find our quotation below:\n\n- PRD-001: 5 × 600.00 USD = 3,000.00 USD (margin 20%)\n- SRV-CONSULT: 1 × 2,875.00 USD = 2,875.00 USD (margin 15%)\n\nSummary:\n- Subtotal: 5,875.00 USD\n- Tax (if applicable): 0.00 USD\n- Shipping: Included\nGrand Total: 5,875.00 USD\n\nDelivery terms: 3-5 business days after payment confirmation\nNotes: Special discount applied to PRD-001 unit cost.\n\nValidity: Prices are valid for 30 days unless otherwise stated.\nPayment terms: 30% advance, balance before shipment (or as agreed).\n\nIf you have any questions or would like to proceed, please contact us.\n\nBest regards,\nSales Team",
    "ar": "عزيزي Acme Corp،\n\nشكرًا على استفساركم. يرجى الاطلاع على عرض الأسعار أدناه:\n\n- PRD-001: 5 × 600.00 USD = 3,000.00 USD (هامش 20%)\n- SRV-CONSULT: 1 × 2,875.00 USD = 2,875.00 USD (هامش 15%)\n\nالملخص:\n- المجموع الفرعي: 5,875.00 USD\n- الضريبة (إن وجدت): 0.00 USD\n- الشحن: مشمول\nالإجمالي الكلي: 5,875.00 USD\n\nشروط التسليم: 3-5 business days after payment confirmation\nملاحظات: Special discount applied to PRD-001 unit cost.\n\nسريان العرض: الأسعار سارية لمدة 30 يومًا ما لم يُذكر خلاف ذلك.\nشروط الدفع: 30% دفعة مقدمة، والباقي قبل الشحن (أو حسب الاتفاق).\n\nإذا كانت لديكم أي أسئلة أو رغبتم في المتابعة، يرجى التواصل معنا.\n\nمع تحيات،\nفريق المبيعات"
  }
}
```

```
```
