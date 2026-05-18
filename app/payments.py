from __future__ import annotations

from typing import Any

from .framework import HTTPException, Router
from .services import serialize_enrollment, serialize_payment, serialize_user
from .store import (
    activate_user_plan,
    create_payment,
    get_payment,
    get_payment_by_ref,
    list_all_payments,
    mark_payment_paid,
    unlock_stage1_for_user,
)


router = Router(prefix="/payments")
admin_router = Router(prefix="/admin")


@router.post("/create-checkout")
def create_checkout(payload: dict[str, Any]) -> dict[str, Any]:
    user_id = str(payload.get("user_id", "me"))
    plan_id = payload.get("plan_id")
    checkout_type = payload.get("type")

    is_stage_unlock = checkout_type == "stage_unlock"
    if checkout_type is not None and checkout_type != "stage_unlock":
        raise HTTPException(status_code=400, detail="type must be 'stage_unlock' when provided")

    if bool(plan_id) == is_stage_unlock:
        raise HTTPException(status_code=400, detail="Provide either plan_id or type='stage_unlock'")

    raw_amount = payload.get("amount", 100 if plan_id else 30)
    try:
        amount = int(raw_amount)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="amount must be an integer") from exc

    if amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be greater than zero")

    currency = str(payload.get("currency", "USD")).upper()
    payment = create_payment(
        user_id=user_id,
        amount=amount,
        currency=currency,
        plan_id=str(plan_id) if plan_id else None,
        for_stage_unlock=is_stage_unlock,
    )

    return {
        "payment_id": payment.id,
        "status": payment.status,
        "payment_gateway_ref": payment.payment_gateway_ref,
        "redirect_url": f"https://payment-gateway.test/pay?ref={payment.payment_gateway_ref}",
        "payment": serialize_payment(payment),
    }


@router.post("/webhook")
def payment_webhook(payload: dict[str, Any]) -> dict[str, Any]:
    payment: Any = None
    if "payment_id" in payload:
        try:
            payment = get_payment(int(payload["payment_id"]))
        except (TypeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail="payment_id must be an integer") from exc
    elif "payment_gateway_ref" in payload:
        payment = get_payment_by_ref(str(payload["payment_gateway_ref"]))
    elif "ref" in payload:
        payment = get_payment_by_ref(str(payload["ref"]))
    else:
        raise HTTPException(status_code=400, detail="payment_id or payment_gateway_ref/ref is required")

    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")

    callback_status = str(payload.get("status", "paid")).lower()
    if callback_status not in {"paid", "success"}:
        raise HTTPException(status_code=400, detail="Only successful callbacks are supported in MVP")

    if payment.status == "paid":
        return {
            "message": "Payment already processed",
            "payment": serialize_payment(payment),
        }

    user = None
    enrollment = None
    if payment.for_stage_unlock:
        enrollment = unlock_stage1_for_user(payment.user_id)
        if enrollment is None:
            raise HTTPException(status_code=404, detail="Enrollment not found for stage unlock")
    elif payment.plan_id is not None:
        user = activate_user_plan(payment.user_id, payment.plan_id)

    mark_payment_paid(payment)

    response: dict[str, Any] = {
        "message": "Payment marked as paid",
        "payment": serialize_payment(payment),
    }
    if user is not None:
        response["user"] = serialize_user(user)
    if enrollment is not None:
        response["enrollment"] = serialize_enrollment(enrollment)
    return response


@admin_router.get("/payments")
def admin_list_payments() -> list[dict[str, Any]]:
    return [serialize_payment(payment) for payment in list_all_payments()]
