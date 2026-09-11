from flask import Blueprint, jsonify, request
from sqlalchemy import select

from ecommerce.database import SessionLocal
from ecommerce.logger import logger
from ecommerce.models import Customer, Order, Product
from ai.investigator import run_investigation
from ai.gemini_investigator import generate_ai_report

api = Blueprint("api", __name__)


@api.route("/", methods=["GET"])
def home():
    return jsonify(
        {
            "message": "AI Production Support Assistant",
            "status": "running",
        }
    )


@api.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})


@api.route("/customers", methods=["GET"])
def get_customers():
    session = SessionLocal()

    try:
        customers = session.scalars(select(Customer)).all()

        result = [
            {
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
            }
            for customer in customers
        ]

        return jsonify(result)

    except Exception as error:
        logger.exception("Failed to retrieve customers: %s", error)

        return jsonify({"error": "Unable to retrieve customers"}), 500

    finally:
        session.close()


@api.route("/products", methods=["GET"])
def get_products():
    session = SessionLocal()

    try:
        products = session.scalars(select(Product)).all()

        result = [
            {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "stock": product.stock,
            }
            for product in products
        ]

        return jsonify(result)

    except Exception as error:
        logger.exception("Failed to retrieve products: %s", error)

        return jsonify({"error": "Unable to retrieve products"}), 500

    finally:
        session.close()


@api.route("/orders", methods=["GET"])
def get_orders():
    session = SessionLocal()

    try:
        orders = session.scalars(select(Order)).all()

        result = [
            {
                "id": order.id,
                "customer_id": order.customer_id,
                "product_id": order.product_id,
                "status": order.status,
            }
            for order in orders
        ]

        return jsonify(result)

    except Exception as error:
        logger.exception("Failed to retrieve orders: %s", error)

        return jsonify({"error": "Unable to retrieve orders"}), 500

    finally:
        session.close()

@api.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "JSON request body is required"}), 400

    customer_id = data.get("customer_id")
    product_id = data.get("product_id")

    # This field lets us deliberately simulate a production failure.
    simulate_payment_failure = data.get(
        "simulate_payment_failure",
        False,
    )

    if customer_id is None or product_id is None:
        return jsonify(
            {
                "error": "customer_id and product_id are required",
            }
        ), 400

    session = SessionLocal()

    try:
        customer = session.get(Customer, customer_id)
        product = session.get(Product, product_id)

        if customer is None:
            logger.warning(
                "Order rejected: customer_id=%s does not exist",
                customer_id,
            )

            return jsonify({"error": "Customer not found"}), 404

        if product is None:
            logger.warning(
                "Order rejected: product_id=%s does not exist",
                product_id,
            )

            return jsonify({"error": "Product not found"}), 404

        if product.stock <= 0:
            logger.error(
                "Order failed: product_id=%s is out of stock",
                product_id,
            )

            return jsonify({"error": "Product is out of stock"}), 409

        logger.info(
            "Order request received: customer_id=%s product_id=%s",
            customer_id,
            product_id,
        )

        if simulate_payment_failure:
            failed_order = Order(
                customer_id=customer_id,
                product_id=product_id,
                status="Pending",
            )

            session.add(failed_order)
            session.commit()
            session.refresh(failed_order)

            logger.error(
                "Payment Gateway Timeout: order_id=%s "
                "customer_id=%s product_id=%s",
                failed_order.id,
                customer_id,
                product_id,
            )

            logger.error(
                "Order confirmation failed: order_id=%s remains Pending",
                failed_order.id,
            )

            return jsonify(
                {
                    "error": "Payment service unavailable",
                    "order_id": failed_order.id,
                    "order_status": failed_order.status,
                }
            ), 503

        order = Order(
            customer_id=customer_id,
            product_id=product_id,
            status="Completed",
        )

        product.stock -= 1

        session.add(order)
        session.commit()
        session.refresh(order)

        logger.info(
            "Order completed successfully: order_id=%s",
            order.id,
        )

        return jsonify(
            {
                "message": "Order created successfully",
                "order": {
                    "id": order.id,
                    "customer_id": order.customer_id,
                    "product_id": order.product_id,
                    "status": order.status,
                },
            }
        ), 201

    except Exception as error:
        session.rollback()

        logger.exception(
            "Unexpected order-processing error: %s",
            error,
        )

        return jsonify(
            {
                "error": "Unexpected order-processing error",
            }
        ), 500

    finally:
        session.close()

@api.route("/investigate", methods=["POST"])
def investigate_incident():
    try:
        logger.info("Incident investigation started")
        report = run_investigation()
        logger.info(
            "Incident investigation completed: %s pending orders, $%s at risk",
            report["evidence"]["pending_order_count"],
            report["evidence"]["revenue_at_risk"],
        )
        return jsonify(report), 200
    except Exception as error:
        logger.exception("Incident investigation failed: %s", error)
        return jsonify({"error": "Incident investigation failed"}), 500


@api.route("/investigate/ai", methods=["POST"])
def investigate_incident_with_ai():
    try:
        logger.info("AI incident investigation started")
        report = generate_ai_report()
        logger.info(
            "AI incident investigation completed: confidence=%s severity=%s",
            report["confidence_score"],
            report["impact_severity"],
        )
        return jsonify(report), 200
    except ValueError as error:
        logger.error("AI configuration error: %s", error)
        return jsonify({"error": str(error)}), 500
    except Exception as error:
        logger.exception("AI incident investigation failed: %s", error)
        return jsonify({"error": "AI incident investigation failed"}), 500


# @api.route("/investigate", methods=["POST"])
# def investigate_incident():
#     try:
#         logger.info("Incident investigation started")

#         report = run_investigation()

#         logger.info(
#             "Incident investigation completed with confidence=%s",
#             report["confidence_score"],
#         )

#         return jsonify(report), 200

#     except Exception as error:
#         logger.exception(
#             "Incident investigation failed: %s",
#             error,
#         )

#         return jsonify(
#             {
#                 "error": "Incident investigation failed",
#             }
#         ), 500
# @api.route("/investigate/ai", methods=["POST"])
# def investigate_incident_with_ai():
#     try:
#         logger.info("AI incident investigation started")

#         report = generate_ai_report()

#         logger.info("AI incident investigation completed")

#         return jsonify(
#             {
#                 "report": report,
#             }
#         ), 200

#     except ValueError as error:
#         logger.error(
#             "AI configuration error: %s",
#             error,
#         )

#         return jsonify(
#             {
#                 "error": str(error),
#             }
#         ), 500

#     except Exception as error:
#         logger.exception(
#             "AI incident investigation failed: %s",
#             error,
#         )

#         return jsonify(
#             {
#                 "error": "AI incident investigation failed",
#             }
#         ), 500