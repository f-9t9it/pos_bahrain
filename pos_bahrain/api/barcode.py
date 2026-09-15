import frappe
import io
import barcode
from barcode.writer import SVGWriter

@frappe.whitelist()
def generate_barcode_svg(data: str, code_type: str = "code128") -> str:
    barcode_class = barcode.get_barcode_class(code_type)
    byte_stream = io.BytesIO()
    barcode_instance = barcode_class(data, writer=SVGWriter())
    barcode_instance.write(byte_stream)
    svg_string = byte_stream.getvalue().decode("utf-8")
    if "<?xml" in svg_string:
        svg_string = svg_string.split("?>", 1)[-1].strip()
    return svg_string
