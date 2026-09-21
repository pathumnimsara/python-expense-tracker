import customtkinter as ctk
import json
from datetime import datetime


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


app = ctk.CTk()
app.title("BudgetAnalyzer")
app.geometry("1050x780")
app.resizable(False, False)

FILE_NAME = "expenses.json"

expenses = []

categories = [
    "Food",
    "Transport",
    "Education",
    "Shopping",
    "Bills",
    "Other"
]

payment_methods = [
    "Cash",
    "Card",
    "UPI"
]

category_icons = {
    "Food": "🍔",
    "Transport": "🚗",
    "Education": "📚",
    "Shopping": "🛍",
    "Bills": "💡",
    "Other": "📦"
}


def save_expenses():
    with open(FILE_NAME, "w") as file:
        json.dump(expenses, file, indent=4)


def load_expenses():
    global expenses

    try:
        with open(FILE_NAME, "r") as file:
            expenses = json.load(file)

    except FileNotFoundError:
        expenses = []


def get_total_spent():
    return sum(expense["amount"] for expense in expenses)


def get_monthly_spent():
    current_month = datetime.now().strftime("%Y-%m")

    total = 0

    for expense in expenses:
        if expense.get("date", "").startswith(current_month):
            total += expense["amount"]

    return total


def get_category_total(category):
    return sum(
        expense["amount"]
        for expense in expenses
        if expense["category"] == category
    )


def refresh_dashboard():
    total = get_total_spent()
    monthly = get_monthly_spent()

    total_spent_label.configure(
        text=f"Rs. {total:,.2f}"
    )

    monthly_label.configure(
        text=f"Rs. {monthly:,.2f}"
    )

    budget_left = max(50000 - monthly, 0)

    budget_label.configure(
        text=f"Rs. {budget_left:,.2f}"
    )

    refresh_expenses()
    refresh_categories()


def create_expense_card(expense):
    category = expense["category"]
    amount = expense["amount"]
    note = expense.get("note", "")
    payment = expense.get("payment", "Cash")

    card = ctk.CTkFrame(
        expense_list,
        corner_radius=14,
        fg_color="#151D2D",
        border_width=1,
        border_color="#202B40"
    )

    card.pack(
        fill="x",
        pady=5
    )

    icon_frame = ctk.CTkFrame(
        card,
        width=42,
        height=42,
        corner_radius=12,
        fg_color="#1E2B43"
    )

    icon_frame.pack(
        side="left",
        padx=(12, 10),
        pady=10
    )

    icon_frame.pack_propagate(False)

    ctk.CTkLabel(
        icon_frame,
        text=category_icons.get(category, "📦"),
        font=ctk.CTkFont(size=18)
    ).pack(expand=True)

    details = ctk.CTkFrame(
        card,
        fg_color="transparent"
    )

    details.pack(
        side="left",
        fill="x",
        expand=True,
        pady=9
    )

    ctk.CTkLabel(
        details,
        text=category,
        font=ctk.CTkFont(
            size=14,
            weight="bold"
        )
    ).pack(
        anchor="w"
    )

    description = note if note else "No description"

    ctk.CTkLabel(
        details,
        text=description,
        text_color="#7F8BA3",
        font=ctk.CTkFont(size=11)
    ).pack(
        anchor="w",
        pady=(2, 0)
    )

    badge = ctk.CTkLabel(
        card,
        text=payment.upper(),
        width=55,
        height=20,
        corner_radius=6,
        fg_color="#253452",
        text_color="#8FB4FF",
        font=ctk.CTkFont(
            size=9,
            weight="bold"
        )
    )

    badge.pack(
        side="right",
        padx=8
    )

    amount_label = ctk.CTkLabel(
        card,
        text=f"-Rs. {amount:,.2f}",
        text_color="#FF7272",
        font=ctk.CTkFont(
            size=14,
            weight="bold"
        )
    )

    amount_label.pack(
        side="right",
        padx=(5, 15)
    )


def refresh_expenses():
    for widget in expense_list.winfo_children():
        widget.destroy()

    if not expenses:
        ctk.CTkLabel(
            expense_list,
            text="No expenses yet\nAdd your first expense above",
            text_color="#6F7C92",
            font=ctk.CTkFont(size=13)
        ).pack(pady=35)

        return

    recent_expenses = expenses[-8:]
    recent_expenses.reverse()

    for expense in recent_expenses:
        create_expense_card(expense)


def refresh_categories():
    for widget in category_container.winfo_children():
        widget.destroy()

    totals = {}

    for category in categories:
        totals[category] = get_category_total(category)

    max_value = max(totals.values()) if totals else 0

    for category in categories:
        amount = totals[category]

        row = ctk.CTkFrame(
            category_container,
            fg_color="transparent"
        )

        row.pack(
            fill="x",
            pady=4
        )

        ctk.CTkLabel(
            row,
            text=f"{category_icons.get(category, '📦')}  {category}",
            width=120,
            anchor="w",
            font=ctk.CTkFont(size=11)
        ).pack(side="left")

        bar_background = ctk.CTkFrame(
            row,
            height=8,
            corner_radius=5,
            fg_color="#202A3D"
        )

        bar_background.pack(
            side="left",
            fill="x",
            expand=True,
            padx=8
        )

        bar_background.pack_propagate(False)

        if max_value > 0:
            width_ratio = amount / max_value
            width = max(5, int(250 * width_ratio))

            bar = ctk.CTkFrame(
                bar_background,
                width=width,
                height=8,
                corner_radius=5,
                fg_color="#4F8CFF"
            )

            bar.pack(
                side="left",
                fill="y"
            )

        ctk.CTkLabel(
            row,
            text=f"Rs. {amount:,.0f}",
            width=85,
            anchor="e",
            font=ctk.CTkFont(
                size=10,
                weight="bold"
            )
        ).pack(side="right")


def add_expense():
    amount_text = amount_entry.get().strip()
    category = category_box.get()
    note = note_entry.get().strip()
    payment = payment_box.get()

    if not amount_text:
        status_label.configure(
            text="Enter an amount",
            text_color="#FF7272"
        )
        return

    try:
        amount = float(amount_text)
    except ValueError:
        status_label.configure(
            text="Enter a valid amount",
            text_color="#FF7272"
        )
        return

    if amount <= 0:
        status_label.configure(
            text="Amount must be greater than 0",
            text_color="#FF7272"
        )
        return

    expense = {
        "amount": amount,
        "category": category,
        "note": note,
        "payment": payment,
        "date": datetime.now().strftime("%Y-%m-%d")
    }

    expenses.append(expense)

    save_expenses()

    amount_entry.delete(0, "end")
    note_entry.delete(0, "end")

    status_label.configure(
        text="Expense added successfully ✓",
        text_color="#4ADE80"
    )

    refresh_dashboard()


load_expenses()


app.configure(
    fg_color="#08101F"
)


# Header

header = ctk.CTkFrame(
    app,
    fg_color="transparent"
)

header.pack(
    fill="x",
    padx=35,
    pady=(28, 10)
)


brand = ctk.CTkFrame(
    header,
    fg_color="transparent"
)

brand.pack(side="left")


ctk.CTkLabel(
    brand,
    text="◈",
    text_color="#4F8CFF",
    font=ctk.CTkFont(
        size=29,
        weight="bold"
    )
).pack(side="left", padx=(0, 8))


brand_text = ctk.CTkFrame(
    brand,
    fg_color="transparent"
)

brand_text.pack(side="left")


ctk.CTkLabel(
    brand_text,
    text="BudgetAnalyzer",
    font=ctk.CTkFont(
        size=22,
        weight="bold"
    )
).pack(anchor="w")


ctk.CTkLabel(
    brand_text,
    text="EXPENSE TRACKER APP",
    text_color="#65748D",
    font=ctk.CTkFont(
        size=9,
        weight="bold"
    )
).pack(anchor="w")


login_card = ctk.CTkFrame(
    header,
    width=135,
    height=46,
    corner_radius=12,
    fg_color="#111B2D",
    border_width=1,
    border_color="#24314A"
)

login_card.pack(
    side="right"
)

login_card.pack_propagate(False)


ctk.CTkLabel(
    login_card,
    text="◉  No bank login",
    font=ctk.CTkFont(
        size=11,
        weight="bold"
    )
).pack(pady=(7, 0))


ctk.CTkLabel(
    login_card,
    text="Free · private by design",
    text_color="#687891",
    font=ctk.CTkFont(size=8)
).pack()


# Month header

month_header = ctk.CTkFrame(
    app,
    fg_color="transparent"
)

month_header.pack(
    fill="x",
    padx=85,
    pady=(10, 8)
)


ctk.CTkLabel(
    month_header,
    text="Expenses · " + datetime.now().strftime("%B"),
    font=ctk.CTkFont(
        size=17,
        weight="bold"
    )
).pack(side="left")


ctk.CTkLabel(
    month_header,
    text="UPI  ·  CARD  ·  CASH",
    text_color="#71819A",
    font=ctk.CTkFont(
        size=9,
        weight="bold"
    )
).pack(side="right")


# Summary cards

summary = ctk.CTkFrame(
    app,
    fg_color="transparent"
)

summary.pack(
    fill="x",
    padx=85,
    pady=4
)


def summary_card(parent, title, value, value_color="#E8EDF7"):
    card = ctk.CTkFrame(
        parent,
        height=78,
        corner_radius=13,
        fg_color="#111A2B",
        border_width=1,
        border_color="#1E2B42"
    )

    card.pack(
        side="left",
        fill="both",
        expand=True,
        padx=4
    )

    card.pack_propagate(False)

    ctk.CTkLabel(
        card,
        text=title,
        text_color="#718099",
        font=ctk.CTkFont(
            size=9,
            weight="bold"
        )
    ).pack(
        anchor="w",
        padx=14,
        pady=(12, 2)
    )

    label = ctk.CTkLabel(
        card,
        text=value,
        text_color=value_color,
        font=ctk.CTkFont(
            size=17,
            weight="bold"
        )
    )

    label.pack(
        anchor="w",
        padx=14
    )

    return label


total_spent_label = summary_card(
    summary,
    "SPENT",
    "Rs. 0.00"
)

budget_label = summary_card(
    summary,
    "BUDGET LEFT",
    "Rs. 50,000.00",
    "#4ADE80"
)

monthly_label = summary_card(
    summary,
    "THIS MONTH",
    "Rs. 0.00"
)


# Main content

content = ctk.CTkFrame(
    app,
    fg_color="transparent"
)

content.pack(
    fill="both",
    expand=True,
    padx=85,
    pady=10
)


left_panel = ctk.CTkFrame(
    content,
    corner_radius=16,
    fg_color="#0F1829",
    border_width=1,
    border_color="#1C2940"
)

left_panel.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(0, 7)
)


right_panel = ctk.CTkFrame(
    content,
    width=285,
    corner_radius=16,
    fg_color="#0F1829",
    border_width=1,
    border_color="#1C2940"
)

right_panel.pack(
    side="right",
    fill="y",
    padx=(7, 0)
)

right_panel.pack_propagate(False)


# Add expense

ctk.CTkLabel(
    left_panel,
    text="Add Expense",
    font=ctk.CTkFont(
        size=15,
        weight="bold"
    )
).pack(
    anchor="w",
    padx=18,
    pady=(15, 8)
)


amount_entry = ctk.CTkEntry(
    left_panel,
    placeholder_text="Amount (Rs.)",
    height=38,
    corner_radius=9,
    fg_color="#151F32",
    border_color="#263650"
)

amount_entry.pack(
    fill="x",
    padx=18,
    pady=4
)


category_box = ctk.CTkComboBox(
    left_panel,
    values=categories,
    height=38,
    corner_radius=9,
    fg_color="#151F32",
    border_color="#263650",
    button_color="#243554"
)

category_box.pack(
    fill="x",
    padx=18,
    pady=4
)

category_box.set("Food")


note_entry = ctk.CTkEntry(
    left_panel,
    placeholder_text="Description",
    height=38,
    corner_radius=9,
    fg_color="#151F32",
    border_color="#263650"
)

note_entry.pack(
    fill="x",
    padx=18,
    pady=4
)


payment_box = ctk.CTkComboBox(
    left_panel,
    values=payment_methods,
    height=38,
    corner_radius=9,
    fg_color="#151F32",
    border_color="#263650",
    button_color="#243554"
)

payment_box.pack(
    fill="x",
    padx=18,
    pady=4
)

payment_box.set("Cash")


button_row = ctk.CTkFrame(
    left_panel,
    fg_color="transparent"
)

button_row.pack(
    fill="x",
    padx=18,
    pady=(5, 10)
)


status_label = ctk.CTkLabel(
    button_row,
    text="",
    font=ctk.CTkFont(size=10)
)

status_label.pack(side="left")


ctk.CTkButton(
    button_row,
    text="+  Add Expense",
    width=125,
    height=34,
    corner_radius=9,
    font=ctk.CTkFont(
        size=11,
        weight="bold"
    ),
    command=add_expense
).pack(side="right")


# Recent expenses

ctk.CTkLabel(
    left_panel,
    text="Recent Expenses",
    font=ctk.CTkFont(
        size=15,
        weight="bold"
    )
).pack(
    anchor="w",
    padx=18,
    pady=(2, 6)
)


expense_list = ctk.CTkScrollableFrame(
    left_panel,
    fg_color="transparent",
    scrollbar_button_color="#263650"
)

expense_list.pack(
    fill="both",
    expand=True,
    padx=8,
    pady=(0, 10)
)


# Right panel

ctk.CTkLabel(
    right_panel,
    text="Spending Overview",
    font=ctk.CTkFont(
        size=15,
        weight="bold"
    )
).pack(
    anchor="w",
    padx=18,
    pady=(17, 4)
)


ctk.CTkLabel(
    right_panel,
    text="By category",
    text_color="#687891",
    font=ctk.CTkFont(size=10)
).pack(
    anchor="w",
    padx=18
)


category_container = ctk.CTkFrame(
    right_panel,
    fg_color="transparent"
)

category_container.pack(
    fill="x",
    padx=18,
    pady=12
)


ctk.CTkFrame(
    right_panel,
    height=1,
    fg_color="#202C42"
).pack(
    fill="x",
    padx=18,
    pady=5
)


ctk.CTkLabel(
    right_panel,
    text="Quick Stats",
    font=ctk.CTkFont(
        size=13,
        weight="bold"
    )
).pack(
    anchor="w",
    padx=18,
    pady=(10, 5)
)


ctk.CTkLabel(
    right_panel,
    text="💰  Track every expense\n\n"
         "📊  Understand your spending\n\n"
         "🔒  Your data stays local",
    justify="left",
    text_color="#7D8BA2",
    font=ctk.CTkFont(size=10),
    anchor="w"
).pack(
    anchor="w",
    padx=18
)


refresh_dashboard()

app.mainloop()