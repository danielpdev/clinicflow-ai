# Pregătire pentru interviu — ClinicFlow AI

Roluri țintă: Applied AI / Python Backend / Healthtech.

## Prezentare de 90 de secunde

1. Explică problema concretă și cine folosește rezultatul.
2. Rulează `make demo` sau fluxul din UI.
3. Arată testul pentru un caz de eșec, apoi explică mecanismul din cod.
4. Spune ce limite are demonstrația și ce ai construi pentru producție.

Decizia de explicat: A suggested appointment is not a booking. A conditional database update claims the slot; the booking and idempotency key commit in the same transaction. Cancellation releases only the slot still owned by that booking.

## Cinci întrebări

1. Cum previi rezervările duble?
2. De ce idempotency key trebuie legat de payload?
3. Ce se întâmplă când anularea și rezervarea concurează?
4. Ce poate face modelul și ce impune baza de date?
5. Cum ai trata fusurile orare?

## Exercițiu înainte de a aplica

Add timezone-aware slot generation and a real patient identity boundary.

Alege o parte mică a acestei modificări, implementeaz-o personal, adaugă un test care verifică comportamentul și descrie rezultatul într-un commit real. Nu declara că ai înțeles sau construit singur o parte pe care nu o poți explica.

## Checklist personal

- [ ] Pot porni proiectul dintr-un checkout curat.
- [ ] Pot urmări cererea până la rezultatul salvat.
- [ ] Pot explica diferența dintre fixture și model local.
- [ ] Pot demonstra un eșec și recuperarea lui.
- [ ] Am făcut o modificare proprie și o pot explica în engleză.

Aceste puncte necesită review-ul tău; nu au fost bifate automat.
