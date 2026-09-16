import frappe
import io
import barcode
from barcode.writer import SVGWriter

@frappe.whitelist()
def generate_barcode_svg(data: str, code_type: str = "code128", height: float = 10, width: float = 0.2, font_size: int = 8, text_distance: float = 1) -> str:
    barcode_class = barcode.get_barcode_class(code_type)
    byte_stream = io.BytesIO()
    barcode_instance = barcode_class(data, writer=SVGWriter())
    barcode_instance.write(byte_stream,options={
        "module_width": width,
        "module_height": height,
        "font_size": font_size,
        "text_distance": text_distance
    })
    svg_string = byte_stream.getvalue().decode("utf-8")
    if "<?xml" in svg_string:
        svg_string = svg_string.split("?>", 1)[-1].strip()
    return svg_string
