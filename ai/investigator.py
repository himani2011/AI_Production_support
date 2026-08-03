from collections import Counter
from pathlib import Path

from sqlalchemy import select

from ecommerce.database import SessionLocal
from ecommerce.models import Order


PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_FILE = PROJECT_ROOT / "logs" / "application.log"
DOCS_DIRECTORY = PROJECT_ROOT / "docs"


def read_log_file() -> list[str]:
    if not LOG_FILE.exists():
        return []

    return LOG_FILE.read_text(
        encoding="utf-8",
    ).splitlines()


def extract_problem_lines(
    log_lines: list[str],
) -> list[str]:
    problem_lines = []

    for line in log_lines:
        if " ERROR " in line or " WARNING " in line:
            problem_lines.append(line)

    return problem_lines


def detect_error_types(
    problem_lines: list[str],
) -> dict[str, int]:
    detected_errors = []

    for line in problem_lines:
        lower_line = line.lower()

        if "payment gateway timeout" in lower_line:
            detected_errors.append("Payment Gateway Timeout")

        elif "out of stock" in lower_line:
            detected_errors.append("Out of Stock")

        elif "customer" in lower_line and "does not exist" in lower_line:
            detected_errors.append("Customer Not Found")

        elif "product" in lower_line and "does not exist" in lower_line:
            detected_errors.append("Product Not Found")

        else:
            detected_errors.append("Other Application Error")

    return dict(Counter(detected_errors))


def get_pending_orders() -> list[dict]:
    session = SessionLocal()

    try:
        statement = select(Order).where(
            Order.status == "Pending"
        )

        orders = session.scalars(statement).all()

        return [
            {
                "id": order.id,
                "customer_id": order.customer_id,
                "product_id": order.product_id,
                "status": order.status,
            }
            for order in orders
        ]

    finally:
        session.close()


def retrieve_documentation(
    detected_errors: dict[str, int],
) -> dict:
    if "Payment Gateway Timeout" in detected_errors:
        document_name = "Payment_Runbook.txt"

    elif "Out of Stock" in detected_errors:
        document_name = "Order_Service.txt"

    else:
        document_name = "Database_Guide.txt"

    document_path = DOCS_DIRECTORY / document_name

    if not document_path.exists():
        return {
            "document": None,
            "content": "No documentation was found.",
        }

    return {
        "document": document_name,
        "content": document_path.read_text(
            encoding="utf-8",
        ),
    }


def determine_root_cause(
    detected_errors: dict[str, int],
    pending_orders: list[dict],
) -> tuple[str, str, int]:
    if "Payment Gateway Timeout" in detected_errors:
        root_cause = (
            "The payment service timed out while processing "
            "customer orders."
        )

        impact = (
            f"{len(pending_orders)} order(s) are currently "
            "in Pending status."
        )

        confidence = 90

    elif "Out of Stock" in detected_errors:
        root_cause = (
            "An order was attempted for a product with "
            "no available inventory."
        )

        impact = "The affected customer could not place the order."
        confidence = 95

    elif detected_errors:
        root_cause = (
            "Application errors were detected, but more evidence "
            "is required to determine the exact cause."
        )

        impact = "One or more application operations may have failed."
        confidence = 55

    else:
        root_cause = "No significant errors were found."
        impact = "No confirmed business impact was detected."
        confidence = 25

    return root_cause, impact, confidence


def run_investigation() -> dict:
    log_lines = read_log_file()
    problem_lines = extract_problem_lines(log_lines)
    detected_errors = detect_error_types(problem_lines)
    pending_orders = get_pending_orders()

    documentation = retrieve_documentation(
        detected_errors
    )

    root_cause, impact, confidence = determine_root_cause(
        detected_errors,
        pending_orders,
    )

    return {
        "incident_summary": (
            f"Found {len(problem_lines)} warning or error "
            "log entries."
        ),
        "detected_errors": detected_errors,
        "root_cause": root_cause,
        "business_impact": impact,
        "confidence_score": confidence,
        "pending_orders": pending_orders,
        "supporting_document": documentation["document"],
        "recommended_actions": [
            "Review the relevant runbook.",
            "Check the payment provider's availability.",
            "Review pending orders before retrying payment.",
            "Escalate the incident if failures continue.",
        ],
        "problem_log_entries": problem_lines[-10:],
    }


if __name__ == "__main__":
    report = run_investigation()

    for key, value in report.items():
        print(f"\n{key}:")
        print(value)