"""The database, not the LLM, owns availability and booking invariants."""

import json
import tempfile
import uuid
from pathlib import Path
from sqlalchemy import String, UniqueConstraint, select, update
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, Field
from app.db import Base, database


class Slot(Base):
    __tablename__ = "slots"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    clinician: Mapped[str]
    starts_at: Mapped[str]
    booking_id: Mapped[str | None]


class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (UniqueConstraint("request_key"),)
    id: Mapped[str] = mapped_column(String, primary_key=True)
    slot_id: Mapped[str]
    patient: Mapped[str]
    request_key: Mapped[str]
    status: Mapped[str]


class Intent(BaseModel):
    action: str = Field(pattern="^(search|propose|clarify)$")
    slot_id: str | None = None
    message: str


class Clinic:
    def __init__(self, url=None):
        self.engine, self.sessions = database(url)
        with self.sessions.begin() as s:
            if not s.get(Slot, "slot-1"):
                for i, hour in enumerate(["09:00", "10:00", "11:00", "14:00"], 1):
                    s.add(
                        Slot(
                            id=f"slot-{i}",
                            clinician="Dr. Demo Rivera",
                            starts_at=f"2030-06-17T{hour}:00+02:00",
                            booking_id=None,
                        )
                    )

    def slots(self):
        with self.sessions() as s:
            return [
                dict(id=x.id, clinician=x.clinician, starts_at=x.starts_at, available=x.booking_id is None)
                for x in s.scalars(select(Slot).order_by(Slot.starts_at))
            ]

    def book(self, slot_id, patient, request_key, confirmed=False):
        if not confirmed:
            raise PermissionError("explicit patient confirmation is required")
        if not patient.strip() or not request_key.strip():
            raise ValueError("patient and idempotency key required")
        try:
            with self.sessions.begin() as s:
                old = s.scalar(select(Booking).where(Booking.request_key == request_key))
                if old:
                    if old.slot_id != slot_id or old.patient != patient:
                        raise ValueError("idempotency key payload conflict")
                    return self._booking(old)
                bid = str(uuid.uuid4())
                claimed = s.execute(
                    update(Slot).where(Slot.id == slot_id, Slot.booking_id.is_(None)).values(booking_id=bid)
                )
                if claimed.rowcount != 1:
                    raise ValueError("slot unavailable")
                b = Booking(
                    id=bid, slot_id=slot_id, patient=patient, request_key=request_key, status="confirmed"
                )
                s.add(b)
                return self._booking(b)
        except IntegrityError:
            with self.sessions() as s:
                old = s.scalar(select(Booking).where(Booking.request_key == request_key))
                if old and old.slot_id == slot_id and old.patient == patient:
                    return self._booking(old)
            raise ValueError("booking conflict; refresh availability") from None

    @staticmethod
    def _booking(b):
        return dict(id=b.id, slot_id=b.slot_id, patient=b.patient, status=b.status)

    def cancel(self, booking_id, confirmed=False):
        if not confirmed:
            raise PermissionError("explicit cancellation confirmation required")
        with self.sessions.begin() as s:
            b = s.get(Booking, booking_id)
            if not b:
                raise ValueError("unknown booking")
            s.execute(
                update(Slot)
                .where(Slot.id == b.slot_id, Slot.booking_id == booking_id)
                .values(booking_id=None)
            )
            b.status = "cancelled"
            return self._booking(b)

    def bookings(self):
        with self.sessions() as s:
            return [self._booking(b) for b in s.scalars(select(Booking))]

    def suggest(self, message, mode="fixture"):
        slots = self.slots()
        if mode == "fixture":
            available = next((s for s in slots if s["available"]), None)
            return dict(
                action="propose" if available else "clarify",
                slot_id=available["id"] if available else None,
                message="Deterministic demo: please confirm the first available slot.",
                mode="fixture",
            )
        from app.local_model import generate

        response = generate(
            "You are a scheduling assistant, not a clinician. Never give medical advice. Choose a listed available slot only when the request is specific; otherwise clarify. You cannot book. Slots: "
            + json.dumps(slots)
            + "\nUser: "
            + message,
            schema=Intent.model_json_schema(),
        )
        intent = Intent.model_validate_json(response["text"])
        if intent.action == "propose" and intent.slot_id not in [s["id"] for s in slots if s["available"]]:
            raise ValueError("model proposed an unavailable or unknown slot")
        return dict(**intent.model_dump(), mode="local-model", model=response["model"])


def demo(mode="fixture"):
    with tempfile.TemporaryDirectory() as d:
        c = Clinic("sqlite:///" + str(Path(d) / "clinic.sqlite"))
        suggestion = c.suggest("Find the earliest appointment on June 17, 2030", mode)
        b = c.book("slot-1", "Alex Demo", "demo-request", confirmed=True)
        replay = c.book("slot-1", "Alex Demo", "demo-request", confirmed=True)
        try:
            c.book("slot-1", "Sam Demo", "other-request", confirmed=True)
        except ValueError as exc:
            conflict = str(exc)
        return dict(suggestion=suggestion, booking=b, replay=replay, conflict=conflict, slots=c.slots())


def evaluate(mode="fixture"):
    from concurrent.futures import ThreadPoolExecutor

    with tempfile.TemporaryDirectory() as d:
        c = Clinic("sqlite:///" + str(Path(d) / "race.sqlite"))

        def attempt(i):
            try:
                c.book("slot-1", f"Patient {i}", f"key-{i}", True)
                return True
            except ValueError:
                return False

        with ThreadPoolExecutor(max_workers=8) as pool:
            wins = sum(pool.map(attempt, range(16)))
        result = {"passed": wins == 1, "concurrent_attempts": 16, "confirmed_bookings": wins}
        if mode == "local":
            result["local_model_demo"] = demo("local")["suggestion"]
        return result
