from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import logging


# ----------------------------------------------------
# 1. FASTAPI INITIALIZATION
# ----------------------------------------------------
app = FastAPI(title="Quotation Service")



# ----------------------------------------------------
# 2. Pydantic Models
# ----------------------------------------------------
class Client(BaseModel):
    name: str
    contact: str
    lang: str = "en"   # en or ar


class Item(BaseModel):
    sku: str
    qty: int
    unit_cost: float
    margin_pct: float


class QuoteRequest(BaseModel):
    client: Client
    currency: str
    items: List[Item]
    delivery_terms: str
    notes: Optional[str] = None


# ----------------------------------------------------
# 3. Price Calculation
# ----------------------------------------------------
def calculate_totals(items: List[Item]):
    line_items_output = []
    grand_total = 0

    for item in items:
        selling_price = item.unit_cost * (1 + item.margin_pct / 100) 
        line_total = selling_price * item.qty
        grand_total += line_total

        line_items_output.append({
            "sku": item.sku,
            "qty": item.qty,
            "unit_cost": round(item.unit_cost, 2),
            "margin_pct": item.margin_pct,
            "selling_price_per_unit": round(selling_price, 2),
            "line_total": round(line_total, 2),
        })

    return line_items_output, round(grand_total, 2)


# ----------------------------------------------------
# 4. LLM (Gemini)
# ----------------------------------------------------
def generate_email(client_name, items, currency, grand_total, delivery, notes):
   
    try:
        # Build itemised lines
        lines_en = []
        lines_ar = []
        subtotal = 0.0
        for it in items:
            sku = it.get("sku", "")
            qty = it.get("qty", 0)
            unit_price = float(it.get("selling_price_per_unit", 0.0))
            line_total = float(it.get("line_total", 0.0))
            margin = it.get("margin_pct", 0)
            subtotal += line_total

            lines_en.append(f"- {sku}: {qty} × {unit_price:,.2f} {currency} = {line_total:,.2f} {currency} (margin {margin}%)")
            lines_ar.append(f"- {sku}: {qty} × {unit_price:,.2f} {currency} = {line_total:,.2f} {currency} (هامش {margin}%)")

        items_section_en = "\n".join(lines_en) if lines_en else "No line items."
        items_section_ar = "\n".join(lines_ar) if lines_ar else "لا توجد بنود."

        # Basic summary (tax/shipping left as placeholders)
        tax = 0.00
        shipping = "Included"  # or specify "To be quoted" / actual value
        shipping_ar = "مشمول" if shipping.lower() == "included" else shipping

        notes_section_en = f"\nNotes: {notes}" if notes else ""
        notes_section_ar = f"\nملاحظات: {notes}" if notes else ""

        email_en = (
            f"Dear {client_name},\n\n"
            "Thank you for your inquiry. Please find our quotation below:\n\n"
            f"{items_section_en}\n\n"
            "Summary:\n"
            f"- Subtotal: {subtotal:,.2f} {currency}\n"
            f"- Tax (if applicable): {tax:,.2f} {currency}\n"
            f"- Shipping: {shipping}\n"
            f"Grand Total: {grand_total:,.2f} {currency}\n\n"
            f"Delivery terms: {delivery}\n"
            f"{notes_section_en}\n\n"
            "Validity: Prices are valid for 30 days unless otherwise stated.\n"
            "Payment terms: 30% advance, balance before shipment (or as agreed).\n\n"
            "If you have any questions or would like to proceed, please contact us.\n\n"
            "Best regards,\nSales Team"
        )

        email_ar = (
            f"عزيزي {client_name},\n\n"
            "شكرًا على استفساركم. يرجى الاطلاع على عرض الأسعار أدناه:\n\n"
            f"{items_section_ar}\n\n"
            "الملخص:\n"
            f"- المجموع الفرعي: {subtotal:,.2f} {currency}\n"
            f"- الضريبة (إن وجدت): {tax:,.2f} {currency}\n"
            f"- الشحن: {shipping_ar}\n"
            f"الإجمالي الكلي: {grand_total:,.2f} {currency}\n\n"
            f"شروط التسليم: {delivery}\n"
            f"{notes_section_ar}\n\n"
            "سريان العرض: الأسعار سارية لمدة 30 يومًا ما لم يُذكر خلاف ذلك.\n"
            "شروط الدفع: 30% دفعة مقدمة، والباقي قبل الشحن (أو حسب الاتفاق).\n\n"
            "إذا كانت لديكم أي أسئلة أو رغبتم في المتابعة، يرجى التواصل معنا.\n\n"
            "مع تحيات،\nفريق المبيعات"
        )

        return {"en": email_en, "ar": email_ar}

    except Exception:
        logging.exception("Failed to build email draft")
        return {
            "en": f"Dear {client_name},\n\nPlease find the quotation. Total: {grand_total:.2f} {currency}.",
            "ar": f"عزيزي {client_name}،\n\nيرجى الاطلاع على العرض. الإجمالي: {grand_total:.2f} {currency}."
        }


# ----------------------------------------------------
# 5. API ENDPOINT (FastAPI)
# ----------------------------------------------------
@app.post("/quote")
def generate_quote(request: QuoteRequest):

    # 1. calculate prices
    line_items, grand_total = calculate_totals(request.items)

    # 2. generate email
    email_draft = generate_email(
        client_name=request.client.name,
        items=line_items,
        currency=request.currency,
        grand_total=grand_total,
        delivery=request.delivery_terms,
        notes=request.notes
    )

    # 3. return output JSON
    return {
        "currency": request.currency,
        "line_items": line_items,
        "grand_total": grand_total,
        "email_draft": email_draft
    }


# ----------------------------------------------------
# 6. Ping Endpoint
# ----------------------------------------------------
@app.get("/")
def root():
    return {"status": "ok", "message": "Quotation Service is running."}


