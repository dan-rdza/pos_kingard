# printer/printer.py
import win32print
import datetime
import os
from PIL import Image

class TicketPrinter:
    def __init__(self, printer_name=None, paper_width_mm=58, logo_path="assets/images/logo.bmp"):
        """
        Inicializa el printer.
        :param printer_name: Nombre de la impresora instalada en Windows.
                             Si None, usa la impresora predeterminada.
        :param paper_width_mm: 58 o 80 mm (afecta ancho de caracteres).
        :param logo_path: Ruta al archivo BMP monocromo (logo).
        """
        self.printer_name = printer_name or win32print.GetDefaultPrinter()
        self.paper_width = 48 #32 if paper_width_mm == 58 else 48
        self.logo_path = logo_path

    def _send(self, raw_bytes: bytes):
        """Envía bytes RAW al spooler de Windows."""
        hPrinter = win32print.OpenPrinter(self.printer_name)
        try:
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("POS Ticket", None, "RAW"))
            win32print.StartPagePrinter(hPrinter)
            win32print.WritePrinter(hPrinter, raw_bytes)
            win32print.EndPagePrinter(hPrinter)
            win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)

    def _text_line(self, text: str = "", align="left", bold=False, font_size="normal") -> bytes:
        """
        Devuelve una línea formateada en ESC/POS.
        :param text: Texto a imprimir.
        :param align: left, center, right.
        :param bold: True/False.
        :param font_size: "small", "normal", "large", "double"
        """
        cmds = b""
        
        # Alineación
        if align == "center":
            cmds += b"\x1b\x61\x01"
        elif align == "right":
            cmds += b"\x1b\x61\x02"
        else:
            cmds += b"\x1b\x61\x00"
        
        # Negrita
        cmds += b"\x1b\x45" + (b"\x01" if bold else b"\x00")
        
        # Tamaño de fuente
        if font_size == "small":
            # Fuente pequeña - Font B
            cmds += b"\x1b\x4d\x01"
        elif font_size == "large":
            # Texto grande (doble altura)
            cmds += b"\x1b\x21\x10"  # Solo doble altura
        elif font_size == "double":
            # Doble altura y ancho
            cmds += b"\x1d\x21\x11"
        else:  # normal
            # Tamaño normal - Font A
            cmds += b"\x1b\x4d\x00"
            cmds += b"\x1d\x21\x00"
        
        return cmds + text.encode("cp437", errors="replace") + b"\n"

    def _cut(self) -> bytes:
        """Comando de corte."""
        return b"\x1dV\x00"

    def _print_logo(self) -> bytes:
        """Imprime logo usando método estándar ESC/POS."""
        if not os.path.exists(self.logo_path):
            return b""
        
        try:
            with Image.open(self.logo_path) as img:
                # Convertir a monocromo
                img = img.convert('1')
                
                # Redimensionar (ancho máximo según tamaño de papel)
                max_width = 256           
                if img.width > max_width:
                    ratio = max_width / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                
                #print(f"Datos Imagen\nImg Width: {img.width }\nMax Width: {max_width}\nRatio: {ratio}\nNew Height: {new_height}")

                # Convertir usando nuestro método propio
                return self._image_to_escpos(img)
                
        except Exception as e:
            print(f"Error procesando logo: {e}")
            return b""

    def _image_to_escpos(self, img: Image.Image) -> bytes:
        """Convierte imagen PIL a formato ESC/POS (compatible con la mayoría de impresoras)."""
        width, height = img.size
        width_bytes = (width + 7) // 8
        
        # Comando ESC/POS para imagen raster (GS v 0)
        header = b"\x1b\x61\x01"  # Centrar
        header += b"\x1d\x76\x30\x00"  # GS v 0
        
        # Añadir dimensiones (little-endian)
        header += width_bytes.to_bytes(2, 'little')
        header += height.to_bytes(2, 'little')
        
        # Convertir pixels a datos binarios
        data = bytearray()
        for y in range(height):
            for x in range(0, width, 8):
                byte = 0
                for bit in range(8):
                    if x + bit < width:
                        pixel = img.getpixel((x + bit, y))
                        # En ESC/POS, 1 = negro, 0 = blanco
                        # En PIL '1' mode, 0 = negro, 255 = blanco
                        if pixel == 0:  # Negro
                            byte |= 1 << (7 - bit)
                data.append(byte)
        
        return header + bytes(data)



    def print_ticket(self, header: dict, items: list, totals: dict, payment_method: str, business: dict, print_logo: bool = True):
        """
        Imprime un ticket con formato profesional.
        :param header: {"folio": str, "student": str, "enrollment": str}
        :param items: [{"description": str, "qty": int, "unit_price": float, "tax_rate": float, "print_logo": bool}]
        :param totals: {"subtotal": float, "tax": float, "total": float}
        :param payment_method: str, nombre del método de pago
        :param business: {"name": str, "rfc": str, "address": str, "phone": str, "footer": str}
        """
        lines = b""

        print_logo = all(item.get("print_logo", False) for item in items)
        print(f"Print Logo: {print_logo}")


        # ---------- Logo ----------
        if print_logo:
            logo_data = self._print_logo()
            
            if logo_data:
                lines += logo_data                

        # ---------- Encabezado ----------       
        lines += self._text_line("PREESCOLAR", align="center", bold=True) 
        lines += self._text_line(business.get("nombre", "NEGOCIO"), align="center", bold=True, font_size="large")
        lines += self._text_line(business.get("clave", ""), align="center", bold=True) 
        lines += b"\n" 

        if business.get("title"):
            lines += self._text_line(f"{business['title']}", align="center", font_size="medium")
        if business.get("rfc"):
            lines += self._text_line(f"RFC: {business['rfc']}", align="center", font_size="medium")
        if business.get("direccion"):
            lines += self._text_line(business["direccion"], align="center", font_size="medium")
        if business.get("contacto"):
            lines += self._text_line(f"{business['contacto']}", align="center", font_size="medium")
        lines += b"\n"
        lines += self._text_line("-" * self.paper_width)
        lines += b"\n" 

        # ---------- Datos Generales ----------
        folio = header.get("folio", "")
        fecha = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        lines += self._text_line(f"FOLIO: {folio}".ljust(self.paper_width - len(fecha)) + fecha, align="left", bold=True)        

        student = header.get("student", "")
        enrollment = header.get("enrollment", "")
        lines += self._text_line(f"MATRICULA: {enrollment}", align="left")        
        lines += self._text_line(f"ALUMNO: {student.upper()}", align="left")        
        lines += b"\n"   

        # ---------- Encabezado tabla ----------
        lines += self._text_line("-" * self.paper_width)
        lines += self._text_line("DESCRIPCION                   P.U.     IMPORTE", align="left", bold=True)
        lines += self._text_line("-" * self.paper_width)

        # ---------- Items ----------
        for item in items:
            qty = str(item["qty"]).ljust(2)
            desc = item["description"][:20].ljust(22)            
            pu = f"${item['unit_price']:,.2f}".rjust(10)
            line_total = f"${item['qty'] * item['unit_price']:,.2f}".rjust(12)
            lines += self._text_line(f"{qty}{desc}{pu}{line_total}", align="left")

        lines += self._text_line("-" * self.paper_width)

        # ---------- Totales ----------
        lines += self._text_line(f"SUBTOTAL: ${totals['subtotal']:,.2f}".rjust(self.paper_width), align="right")
        lines += self._text_line(f"IVA: ${totals['tax']:,.2f}".rjust(self.paper_width), align="right")
        lines += self._text_line(f"TOTAL: ${totals['total']:,.2f}".rjust(self.paper_width), align="right", bold=True, font_size="large")
        lines += self._text_line("-" * self.paper_width)

        # ---------- Método de pago ----------
        lines += self._text_line(f"Método de Pago: {payment_method}", align="left")
        lines += b"\n"
        
        # ---------- Mensaje final ----------
        lines += self._text_line(business.get("notas01", "¡Gracias por su compra!"), align="center", bold=True)
        lines += self._text_line(business.get("notas02", "¡Gracias por su compra!"), align="center", bold=True)

        # Espacio adicional
        lines += b"\n\n\n"

        # ---------- Corte ----------
        lines += self._cut()

        # Enviar a impresora
        self._send(lines)

    def preview_ticket(self, header: dict, items: list, totals: dict, payment_method: str, business: dict, file_path="ticket_preview.txt"):
        """
        Genera una vista previa del ticket en texto plano (sin ESC/POS).
        """
        lines = []

        # Logo (solo placeholder)
        lines.append("[LOGO]\n")

        # Encabezado
        lines.append(f"{business.get('name', 'NEGOCIO')}\n")
        if business.get("rfc"):
            lines.append(f"RFC: {business['rfc']}\n")
        if business.get("address"):
            lines.append(f"{business['address']}\n")
        if business.get("phone"):
            lines.append(f"Tel: {business['phone']}\n")
        lines.append("-" * self.paper_width + "\n")

        # Folio y fecha
        folio = header.get("folio", "")
        fecha = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        lines.append(f"Venta: {folio}".ljust(self.paper_width - len(fecha)) + fecha + "\n")

        # Alumno
        student = header.get("student", "")
        enrollment = header.get("enrollment", "")
        lines.append(f"Matrícula: {enrollment}\n")
        lines.append(f"Alumno: {student}\n")        
        lines.append("-" * self.paper_width + "\n")

        # Tabla
        lines.append("CONCEPTO            CANT      P.U.      IMPORTE\n")
        lines.append("-" * self.paper_width + "\n")
        for item in items:
            desc = item["description"][:20].ljust(20)
            qty = str(item["qty"]).rjust(4)
            pu = f"{item['unit_price']:.2f}".rjust(10)
            line_total = f"{item['qty'] * item['unit_price']:.2f}".rjust(13)
            lines.append(f"{desc}{qty}{pu}{line_total}\n")

        lines.append("-" * self.paper_width + "\n")

        # Totales
        lines.append(f"SUBTOTAL: {totals['subtotal']:.2f}".rjust(self.paper_width) + "\n")
        lines.append(f"IVA: {totals['tax']:.2f}".rjust(self.paper_width) + "\n")
        lines.append(f"TOTAL: {totals['total']:.2f}".rjust(self.paper_width) + "\n")
        lines.append("-" * self.paper_width + "\n")

        # Método de pago
        lines.append(f"Pago: {payment_method}\n")

        # Footer
        lines.append(business.get("footer", "¡Gracias por su compra!") + "\n")

        preview = "".join(lines)

        # Guardar en archivo
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(preview)

        return preview