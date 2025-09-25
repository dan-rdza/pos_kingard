# printer/printer.py
import win32print
import datetime


class TicketPrinter:
    def __init__(self, printer_name=None, paper_width_mm=58):
        """
        Inicializa el printer.
        :param printer_name: Nombre de la impresora instalada en Windows.
                             Si None, usa la impresora predeterminada.
        :param paper_width_mm: 58 o 80 mm (afecta ancho de caracteres).
        """
        self.printer_name = printer_name or win32print.GetDefaultPrinter()
        self.paper_width = 32 if paper_width_mm == 58 else 48  # caracteres por línea aprox.

    def _send(self, raw_bytes: bytes):
        """Envia bytes RAW al spooler de Windows."""
        hPrinter = win32print.OpenPrinter(self.printer_name)
        try:
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("POS Ticket", None, "RAW"))
            win32print.StartPagePrinter(hPrinter)
            win32print.WritePrinter(hPrinter, raw_bytes)
            win32print.EndPagePrinter(hPrinter)
            win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)

    def _text_line(self, text: str = "", align="left", bold=False) -> bytes:
        """
        Devuelve una línea formateada en ESC/POS.
        :param text: Texto a imprimir.
        :param align: left, center, right.
        :param bold: True/False.
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
        # Texto + salto
        return cmds + text.encode("cp437", errors="replace") + b"\n"

    def _cut(self) -> bytes:
        """Comando de corte."""
        return b"\x1dV\x00"

    def print_ticket(self, header: dict, items: list, totals: dict, payment_method: str, business: dict):
        """
        Imprime un ticket con formato profesional.
        :param header: dict con {"folio": str, "student": str, "enrollment": str}
        :param items: lista de dicts con {"description": str, "qty": int, "unit_price": float, "tax_rate": float}
        :param totals: dict con {"subtotal": float, "tax": float, "total": float}
        :param payment_method: str, nombre del método de pago
        :param business: dict con {"name": str, "rfc": str, "address": str, "phone": str, "footer": str}
        """
        lines = b""

        # ---------- Encabezado ----------
        lines += self._text_line(business.get("name", "NEGOCIO"), align="center", bold=True)
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
        lines += self._text_line(f"Folio: {folio}   {fecha}", align="left")

        # ---------- Alumno ----------
        student = header.get("student", "")
        enrollment = header.get("enrollment", "")
        lines += self._text_line(f"Alumno: {student}", align="left")
        lines += self._text_line(f"Matrícula: {enrollment}", align="left")
        lines += self._text_line("-" * self.paper_width)

        # ---------- Encabezado tabla ----------
        lines += self._text_line("Descripcion     Cant  P.U.  Importe", align="left", bold=True)
        lines += self._text_line("-" * self.paper_width)

        # ---------- Items ----------
        for item in items:
            desc = item["description"][:12].ljust(12)
            qty = str(item["qty"]).rjust(3)
            pu = f"{item['unit_price']:.2f}".rjust(6)
            line_total = f"{item['qty'] * item['unit_price']:.2f}".rjust(8)
            lines += self._text_line(f"{desc}{qty}{pu}{line_total}", align="left")

        lines += self._text_line("-" * self.paper_width)

        # ---------- Totales ----------
        lines += self._text_line(f"SUBTOTAL: {totals['subtotal']:.2f}".rjust(self.paper_width), align="right")
        lines += self._text_line(f"IVA: {totals['tax']:.2f}".rjust(self.paper_width), align="right")
        lines += self._text_line(f"TOTAL: {totals['total']:.2f}".rjust(self.paper_width), align="right", bold=True)
        lines += self._text_line("-" * self.paper_width)

        # ---------- Método de pago ----------
        lines += self._text_line(f"Pago: {payment_method}", align="left")

        # ---------- Mensaje final ----------
        lines += self._text_line(business.get("footer", "¡Gracias por su compra!"), align="center", bold=True)

        # ---------- Corte ----------
        lines += self._cut()

        # Enviar a impresora
        self._send(lines)
