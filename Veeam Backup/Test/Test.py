
import base64

original_string = "administrator:P4$$w.rd1"
encoded_bytes = base64.b64encode(original_string.encode("utf-8"))

print(str(encoded_bytes))