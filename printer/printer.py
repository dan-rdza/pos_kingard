# printer/printer.py
import win32print
import datetime
import os


class TicketPrinter:
    def __init__(self, printer_name=None, paper_width_mm=58, logo_path="assets/logo.bmp"):
        """
        Inicializa el printer.
        :param printer_name: Nombre de la impresora instalada en Windows.
                             Si None, usa la impresora predeterminada.
        :param paper_width_mm: 58 o 80 mm (afecta ancho de caracteres).
        :param logo_path: Ruta al archivo BMP monocromo (logo).
        """
        self.printer_name = printer_name or win32print.GetDefaultPrinter()
        self.paper_width = 32 if paper_width_mm == 58 else 48  # caracteres por línea
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

    def _text_line(self, text: str = "", align="left", bold=False, double_height=False) -> bytes:
        """
        Devuelve una línea formateada en ESC/POS.
        :param text: Texto a imprimir.
        :param align: left, center, right.
        :param bold: True/False.
        :param double_height: Texto más grande (para totales, por ejemplo).
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
        # Tamaño
        if double_height:
            cmds += b"\x1d\x21\x11"  # doble ancho y alto
        else:
            cmds += b"\x1d\x21\x00"
        return cmds + text.encode("cp437", errors="replace") + b"\n"

    def _cut(self) -> bytes:
        """Comando de corte."""
        return b"\x1dV\x00"

    def _print_logo(self) -> bytes:
        """Imprime un logo si existe (formato BMP monocromo)."""
        if not os.path.exists(self.logo_path):
            return b""
        try:
            with open(self.logo_path, "rb") as f:
                data = f.read()
            # Enviamos directo el archivo BMP (solo funciona si la impresora soporta)
            return b"\x1b\x61\x01" + data  # centrado + datos
        except Exception:
            return b""

    def print_ticket(self, header: dict, items: list, totals: dict, payment_method: str, business: dict):
        """
        Imprime un ticket con formato profesional.
        :param header: {"folio": str, "student": str, "enrollment": str}
        :param items: [{"description": str, "qty": int, "unit_price": float, "tax_rate": float}]
        :param totals: {"subtotal": float, "tax": float, "total": float}
        :param payment_method: str, nombre del método de pago
        :param business: {"name": str, "rfc": str, "address": str, "phone": str, "footer": str}
        """
        lines = b""

        # ---------- Logo ----------
        lines += self._print_logo()

        # ---------- Encabezado ----------
        lines += self._text_line(business.get("name", "NEGOCIO"), align="center", bold=True, double_height=True)
        if business.get("rfc"):
            lines += self._text_line(f"RFC: {business['rfc']}", align="center")
        if business.get("address"):
            lines += self._text_line(business["address"], align="center")
        if business.get("phone"):
            lines += self._text_line(f"Tel: {business['phone']}", align="center")
        lines += self._text_line("-" * self.paper_width)

        # ---------- Folio y fecha ----------
        folio = header.get("folio", "")
        fecha = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        lines += self._text_line(f"Folio: {folio}".ljust(self.paper_width - len(fecha)) + fecha, align="left")

        # ---------- Alumno ----------
        student = header.get("student", "")
        enrollment = header.get("enrollment", "")
        lines += self._text_line(f"Alumno: {student}", align="left")
        lines += self._text_line(f"Matrícula: {enrollment}", align="left")
        lines += self._text_line("-" * self.paper_width)

        # ---------- Encabezado tabla ----------
        lines += self._text_line("Descripcion       Cant   P.U.   Importe", align="left", bold=True)
        lines += self._text_line("-" * self.paper_width)

        # ---------- Items ----------
        for item in items:
            desc = item["description"][:15].ljust(15)
            qty = str(item["qty"]).rjust(4)
            pu = f"{item['unit_price']:.2f}".rjust(7)
            line_total = f"{item['qty'] * item['unit_price']:.2f}".rjust(9)
            lines += self._text_line(f"{desc}{qty}{pu}{line_total}", align="left")

        lines += self._text_line("-" * self.paper_width)

        # ---------- Totales ----------
        lines += self._text_line(f"SUBTOTAL: {totals['subtotal']:.2f}".rjust(self.paper_width), align="right")
        lines += self._text_line(f"IVA: {totals['tax']:.2f}".rjust(self.paper_width), align="right")
        lines += self._text_line(f"TOTAL: {totals['total']:.2f}".rjust(self.paper_width), align="right", bold=True, double_height=True)
        lines += self._text_line("-" * self.paper_width)

        # ---------- Método de pago ----------
        lines += self._text_line(f"Pago: {payment_method}", align="left")

        # ---------- Mensaje final ----------
        lines += self._text_line(business.get("footer", "¡Gracias por su compra!"), align="center", bold=True)

        # Espacio adicional
        lines += b"\n\n"

        # ---------- Corte ----------
        lines += self._cut()

        # Enviar a impresora
        print(lines)
        self._send(lines)

# dentro de TicketPrinter

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

