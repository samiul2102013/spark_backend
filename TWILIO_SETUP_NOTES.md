# Twilio Setup Notes for ChargeSafe (Jamaica)

## Credentials Needed from Client
1. **Account SID** — starts with `AC...`
2. **Auth Token** — secret key
3. **Phone Number** OR **Alphanumeric Sender ID** (see below)

## Two Options for Sender

### Option A: Phone Number (~$1/month)
- Buy from Twilio Console → Phone Numbers → Buy a Number
- For Jamaica: Jamaican local numbers NOT available, buy a **US number** with SMS capability
- Works on free trial (limited to verified recipients)
- Can send AND receive replies
- Set in `.env`: `TWILIO_PHONE_NUMBER=+1XXXXXXXXXX`

### Option B: Alphanumeric Sender ID (free)
- Recipients see your brand name (e.g. `SPARK`) instead of a number
- Jamaica SUPPORTS it — no pre-registration needed
- Works on both Digicel and Flow
- **REQUIRES PAID ACCOUNT** — free trial won't work
- Send-only (no replies)
- Set in `.env`: `TWILIO_PHONE_NUMBER=SPARK`
- To set up: Messaging → Services → Create Service → Sender Pool → Add Sender → Alphanumeric Sender ID

## Account Status
- **Free trial**: Can only send to verified numbers (add in Console), limited to 5 SMS/day
- **Paid (credit card added)**: Full sending, Alphanumeric Sender ID works, no limits

## `.env` Variables
```ini
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=SPARK        # or +1XXXXXXXXXX
OTP_MOCK_MODE=False              # True = bypass SMS (000000 code works)
```

## Testing Flow
```bash
# 1. Register user
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "+8801856669532", "full_name": "Test", "household_size": 1, "medical_needs": "", "latitude": 18.0, "longitude": -77.0}'

# 2. Send OTP
curl -X POST http://localhost:8000/api/v1/auth/otp/send/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "+8801856669532"}'

# 3. Check logs for Twilio errors
docker logs spark_backend-django-1 2>&1 | grep -i "twilio\|otp\|sms\|failed"
```

## Common Errors
| Error | Cause | Fix |
|---|---|---|
| `20003` | Trial account, not paid | Add credit card in Twilio Billing |
| `21211` | Invalid `from_` number | Check `TWILIO_PHONE_NUMBER` in `.env` |
| `21610` | Unverified destination (trial) | Add recipient number in Console → Verified Caller IDs |
| No SMS but no error | `OTP_MOCK_MODE=True` | Set `OTP_MOCK_MODE=False` |

## Django Models
- User model PK is `phone_number` (CharField, not auto-increment int)
- All API URLs use `<str:user_id>` not `<int:user_id>`

## Workflow for New SMS Provider
1. Get Account SID + Auth Token + Sender (number or alphanumeric)
2. Update `.env` with all 3 values
3. Set `OTP_MOCK_MODE=False`
4. Test with register → send OTP flow
5. Check Docker logs if no SMS arrives
