import io
import qrcode


def generate_batch_qr(batch_id: int) -> bytes:
    tracking_url = (
        f"http://127.0.0.1:8000/api/v1/batches/{batch_id}"
    )

    image = qrcode.make(tracking_url)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")

    return buffer.getvalue()