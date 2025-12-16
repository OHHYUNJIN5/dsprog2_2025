import math
import flet as ft


class CalcButton(ft.ElevatedButton):
    def __init__(self, text, button_clicked, expand=1):
        super().__init__()
        self.text = text
        self.expand = expand
        self.on_click = button_clicked
        self.data = text


class DigitButton(CalcButton):
    def __init__(self, text, button_clicked, expand=1):
        super().__init__(text, button_clicked, expand)
        self.bgcolor = ft.Colors.WHITE24
        self.color = ft.Colors.WHITE


class ActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        super().__init__(text, button_clicked)
        self.bgcolor = ft.Colors.ORANGE
        self.color = ft.Colors.WHITE


class ExtraActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        super().__init__(text, button_clicked)
        self.bgcolor = ft.Colors.BLUE_GREY_100
        self.color = ft.Colors.BLACK


class SciButton(CalcButton):
    def __init__(self, text, button_clicked):
        super().__init__(text, button_clicked)
        self.bgcolor = ft.Colors.BLUE_GREY_300
        self.color = ft.Colors.BLACK


class CalculatorApp(ft.Container):
    def __init__(self):
        super().__init__()
        self.reset()
        self.sci_mode = False
        self.angle_mode = "DEG"  # "DEG" or "RAD"

        self.result = ft.Text(value="0", color=ft.Colors.WHITE, size=24)

        self.width = 350
        self.bgcolor = ft.Colors.BLACK
        self.border_radius = ft.border_radius.all(20)
        self.padding = 20

        self.content = self.build_layout()

    # ---------- UI ----------
    def build_layout(self):
        controls = []

        # Display row
        controls.append(ft.Row(controls=[self.result], alignment="end"))

        # Top utility row (+ SCI toggle)
        controls.append(
            ft.Row(
                controls=[
                    ExtraActionButton(text="SCI", button_clicked=self.button_clicked),
                    ExtraActionButton(text=self.angle_mode, button_clicked=self.button_clicked),
                    ExtraActionButton(text="AC", button_clicked=self.button_clicked),
                    ExtraActionButton(text="+/-", button_clicked=self.button_clicked),
                ]
            )
        )

        # Scientific panel (toggle)
        sci_panel = ft.Column(visible=self.sci_mode, controls=[
            ft.Row(controls=[
                SciButton(text="sin", button_clicked=self.button_clicked),
                SciButton(text="cos", button_clicked=self.button_clicked),
                SciButton(text="tan", button_clicked=self.button_clicked),
                SciButton(text="√", button_clicked=self.button_clicked),
            ]),
            ft.Row(controls=[
                SciButton(text="x²", button_clicked=self.button_clicked),
                SciButton(text="xʸ", button_clicked=self.button_clicked),
                SciButton(text="ln", button_clicked=self.button_clicked),
                SciButton(text="log10", button_clicked=self.button_clicked),
            ]),
            ft.Row(controls=[
                SciButton(text="!", button_clicked=self.button_clicked),
                SciButton(text="π", button_clicked=self.button_clicked),
                SciButton(text="e", button_clicked=self.button_clicked),
                SciButton(text="%", button_clicked=self.button_clicked),
            ]),
        ])
        controls.append(sci_panel)

        # Normal keypad
        controls.extend([
            ft.Row(controls=[
                DigitButton(text="7", button_clicked=self.button_clicked),
                DigitButton(text="8", button_clicked=self.button_clicked),
                DigitButton(text="9", button_clicked=self.button_clicked),
                ActionButton(text="/", button_clicked=self.button_clicked),
            ]),
            ft.Row(controls=[
                DigitButton(text="4", button_clicked=self.button_clicked),
                DigitButton(text="5", button_clicked=self.button_clicked),
                DigitButton(text="6", button_clicked=self.button_clicked),
                ActionButton(text="*", button_clicked=self.button_clicked),
            ]),
            ft.Row(controls=[
                DigitButton(text="1", button_clicked=self.button_clicked),
                DigitButton(text="2", button_clicked=self.button_clicked),
                DigitButton(text="3", button_clicked=self.button_clicked),
                ActionButton(text="-", button_clicked=self.button_clicked),
            ]),
            ft.Row(controls=[
                DigitButton(text="0", expand=2, button_clicked=self.button_clicked),
                DigitButton(text=".", button_clicked=self.button_clicked),
                ActionButton(text="=", button_clicked=self.button_clicked),
                ActionButton(text="+", button_clicked=self.button_clicked),
            ]),
        ])

        return ft.Column(controls=controls)

    def refresh_layout(self):
        self.content = self.build_layout()
        self.update()

    #Logic 
    def button_clicked(self, e):
        data = e.control.data
        # print(f"Button clicked with data = {data}")

        #Toggles
        if data == "SCI":
            self.sci_mode = not self.sci_mode
            self.refresh_layout()
            return

        if data in ("DEG", "RAD"):
            self.angle_mode = "RAD" if self.angle_mode == "DEG" else "DEG"
            self.refresh_layout()
            return

        #Reset/Error handling
        if self.result.value == "Error" or data == "AC":
            self.result.value = "0"
            self.reset()
            self.update()
            return

        #Digits
        if data in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."):
            if self.result.value == "0" or self.new_operand:
                self.result.value = data
                self.new_operand = False
            else:
                self.result.value = self.result.value + data
            self.update()
            return

        #Constants
        if data in ("π", "e"):
            val = math.pi if data == "π" else math.e
            self.result.value = str(self.format_number(val))
            self.new_operand = True
            self.update()
            return

        #Unary scientific operations
        if data in ("sin", "cos", "tan", "√", "x²", "ln", "log10", "!", "%"):
            self.apply_scientific(data)
            self.update()
            return

        #Binary operations (+ - * / xʸ)
        if data in ("+", "-", "*", "/", "xʸ"):
            op = "^" if data == "xʸ" else data
            self.result.value = self.calculate(self.operand1, float(self.result.value), self.operator)
            self.operator = op
            if self.result.value == "Error":
                self.operand1 = 0
            else:
                self.operand1 = float(self.result.value)
            self.new_operand = True
            self.update()
            return

        #Equals
        if data == "=":
            self.result.value = self.calculate(self.operand1, float(self.result.value), self.operator)
            self.reset()
            self.update()
            return

        #Sign
        if data == "+/-":
            try:
                x = float(self.result.value)
                self.result.value = str(self.format_number(-x))
            except Exception:
                self.result.value = "Error"
            self.update()
            return

        self.update()

    def apply_scientific(self, op: str):
        try:
            x = float(self.result.value)

            if op == "%":
                self.result.value = str(self.format_number(x / 100))
                self.reset()
                return

            if op == "√":
                if x < 0:
                    self.result.value = "Error"
                else:
                    self.result.value = str(self.format_number(math.sqrt(x)))
                self.new_operand = True
                return

            if op == "x²":
                self.result.value = str(self.format_number(x * x))
                self.new_operand = True
                return

            if op == "ln":
                if x <= 0:
                    self.result.value = "Error"
                else:
                    self.result.value = str(self.format_number(math.log(x)))
                self.new_operand = True
                return

            if op == "log10":
                if x <= 0:
                    self.result.value = "Error"
                else:
                    self.result.value = str(self.format_number(math.log10(x)))
                self.new_operand = True
                return

            if op in ("sin", "cos", "tan"):
                rad = math.radians(x) if self.angle_mode == "DEG" else x
                if op == "sin":
                    y = math.sin(rad)
                elif op == "cos":
                    y = math.cos(rad)
                else:
                    y = math.tan(rad)
                self.result.value = str(self.format_number(y))
                self.new_operand = True
                return

            if op == "!":
                if x < 0 or (x % 1) != 0:
                    self.result.value = "Error"
                else:
                    n = int(x)
                    if n > 170:
                        self.result.value = "Error"
                    else:
                        self.result.value = str(self.format_number(math.factorial(n)))
                self.new_operand = True
                return

        except Exception:
            self.result.value = "Error"

    def format_number(self, num):
        # -0.0 같은 표시 방지
        if isinstance(num, float) and abs(num) < 1e-12:
            num = 0.0
        if isinstance(num, (int, float)) and (float(num) % 1 == 0):
            return int(num)
        return num

    def calculate(self, operand1, operand2, operator):
        try:
            if operator == "+":
                return self.format_number(operand1 + operand2)
            if operator == "-":
                return self.format_number(operand1 - operand2)
            if operator == "*":
                return self.format_number(operand1 * operand2)
            if operator == "/":
                if operand2 == 0:
                    return "Error"
                return self.format_number(operand1 / operand2)
            if operator == "^":
                # xʸ
                return self.format_number(math.pow(operand1, operand2))
        except Exception:
            return "Error"

        return self.format_number(operand2)

    def reset(self):
        self.operator = "+"
        self.operand1 = 0
        self.new_operand = True


def main(page: ft.Page):
    page.title = "Simple Calculator"
    calc = CalculatorApp()
    page.add(calc)


ft.app(main)
