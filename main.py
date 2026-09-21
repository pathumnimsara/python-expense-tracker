import customtkinter as ctk
import json
from datetime import datetime
from tkinter import messagebox


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


app = ctk.CTk()
app.title("BudgetAnalyzer")
app.geometry("1180x850")
app.minsize(720, 650)


FILE_NAME = "expenses.json"
SETTINGS_FILE = "settings.json"

expenses = []
monthly_budget = 50000.0
mobile_layout = False


C = {
    "bg": "#08101F",
    "panel": "#0F1829",
    "card": "#111A2B",
    "input": "#151F32",
    "border": "#1E2B42",
    "border2": "#263650",
    "text": "#E8EDF7",
    "muted": "#718099",
    "dim": "#52627A",
    "blue": "#4F8CFF",
    "blue_dark": "#17243A",
    "blue_hover": "#223554",
    "green": "#4ADE80",
    "red": "#FF7272",
    "orange": "#FFB86C"
}


default_categories = [
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


def save_settings():
    with open(SETTINGS_FILE, "w") as file:
        json.dump(
            {
                "monthly_budget": monthly_budget
            },
            file,
            indent=4
        )


def load_settings():
    global monthly_budget

    try:
        with open(SETTINGS_FILE, "r") as file:
            data = json.load(file)

        monthly_budget = float(
            data.get("monthly_budget", 50000)
        )

    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        monthly_budget = 50000.0


def load_expenses():
    global expenses

    try:
        with open(FILE_NAME, "r") as file:
            saved = json.load(file)

        expenses = []

        for expense in saved:
            if "amount" not in expense:
                continue

            expense.setdefault("category", "Other")
            expense.setdefault("note", "")
            expense.setdefault("payment", "Cash")
            expense.setdefault("date", "")
            expense.setdefault("time", "")

            expenses.append(expense)

    except (FileNotFoundError, json.JSONDecodeError):
        expenses = []


def get_total_spent():
    return sum(
        float(expense.get("amount", 0))
        for expense in expenses
    )


def get_monthly_spent():
    current_month = datetime.now().strftime("%Y-%m")

    return sum(
        float(expense.get("amount", 0))
        for expense in expenses
        if expense.get("date", "").startswith(current_month)
    )


def get_budget_left():
    return monthly_budget - get_monthly_spent()


def get_all_categories():
    categories = list(default_categories)

    for expense in expenses:
        category = expense.get("category", "").strip()

        if category and category not in categories:
            categories.append(category)

    return categories


def get_category_total(category):
    return sum(
        float(expense.get("amount", 0))
        for expense in expenses
        if expense.get("category") == category
    )


def category_icon(category):
    return category_icons.get(category, "📁")


def format_date_time(expense):
    date_value = expense.get("date", "")
    time_value = expense.get("time", "")

    if not date_value:
        return "Date not available"

    try:
        date_value = datetime.strptime(
            date_value,
            "%Y-%m-%d"
        ).strftime("%d %b %Y")

    except ValueError:
        pass

    if time_value:
        return f"{date_value} · {time_value}"

    return date_value


def set_budget():
    global monthly_budget

    window = ctk.CTkToplevel(app)
    window.title("Set Monthly Budget")
    window.geometry("400x320")
    window.resizable(False, False)
    window.configure(
        fg_color=C["bg"]
    )

    window.transient(app)
    window.grab_set()

    ctk.CTkLabel(
        window,
        text="Set Monthly Budget",
        text_color=C["text"],
        font=ctk.CTkFont(
            size=21,
            weight="bold"
        )
    ).pack(
        pady=(30, 8)
    )

    ctk.CTkLabel(
        window,
        text="Your expenses will automatically reduce this amount.",
        text_color=C["muted"],
        font=ctk.CTkFont(size=11)
    ).pack(
        pady=(0, 18)
    )

    entry = ctk.CTkEntry(
        window,
        height=44,
        corner_radius=10,
        placeholder_text="Monthly budget",
        fg_color=C["input"],
        border_color=C["border2"],
        text_color=C["text"],
        placeholder_text_color=C["muted"]
    )

    entry.pack(
        fill="x",
        padx=30
    )

    entry.insert(
        0,
        str(monthly_budget)
    )

    error_label = ctk.CTkLabel(
        window,
        text="",
        text_color=C["red"]
    )

    error_label.pack(
        pady=8
    )

    def save_budget():
        global monthly_budget

        try:
            value = float(
                entry.get().strip()
            )

        except ValueError:
            error_label.configure(
                text="Enter a valid amount"
            )
            return

        if value <= 0:
            error_label.configure(
                text="Budget must be greater than 0"
            )
            return

        monthly_budget = value

        save_settings()

        window.destroy()

        refresh_dashboard()

        status_label.configure(
            text="Budget updated successfully ✓",
            text_color=C["green"]
        )

    ctk.CTkButton(
        window,
        text="Save Budget",
        height=42,
        corner_radius=10,
        command=save_budget
    ).pack(
        fill="x",
        padx=30,
        pady=5
    )

    ctk.CTkButton(
        window,
        text="Cancel",
        height=38,
        corner_radius=10,
        fg_color=C["blue_dark"],
        hover_color=C["blue_hover"],
        text_color=C["blue"],
        command=window.destroy
    ).pack(
        fill="x",
        padx=30,
        pady=3
    )


def clear_all():
    global expenses
    global monthly_budget

    answer = messagebox.askyesno(
        "Clear All Data",
        "Are you sure you want to clear all expenses\n"
        "and reset the monthly budget?\n\n"
        "This action cannot be undone."
    )

    if not answer:
        return

    expenses = []
    monthly_budget = 0.0

    save_expenses()
    save_settings()

    refresh_dashboard()

    status_label.configure(
        text="All data cleared",
        text_color=C["orange"]
    )


def add_expense():
    amount_text = amount_entry.get().strip()
    category = category_box.get().strip()
    note = note_entry.get().strip()
    payment = payment_box.get()

    if not amount_text:
        status_label.configure(
            text="Enter an amount",
            text_color=C["red"]
        )
        return

    try:
        amount = float(amount_text)

    except ValueError:
        status_label.configure(
            text="Enter a valid amount",
            text_color=C["red"]
        )
        return

    if amount <= 0:
        status_label.configure(
            text="Amount must be greater than 0",
            text_color=C["red"]
        )
        return

    if not category:
        status_label.configure(
            text="Enter a category",
            text_color=C["red"]
        )
        return

    now = datetime.now()

    expenses.append(
        {
            "amount": amount,
            "category": category,
            "note": note,
            "payment": payment,
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%I:%M:%S %p")
        }
    )

    save_expenses()

    amount_entry.delete(0, "end")
    note_entry.delete(0, "end")

    category_box.set("Food")
    payment_box.set("Cash")

    status_label.configure(
        text="Expense added successfully ✓",
        text_color=C["green"]
    )

    refresh_dashboard()


def delete_expense(index):
    if index >= len(expenses):
        return

    expense = expenses[index]

    answer = messagebox.askyesno(
        "Delete Expense",
        f"Delete this expense?\n\n"
        f"{expense.get('category', 'Other')} - "
        f"Rs. {float(expense.get('amount', 0)):,.2f}"
    )

    if not answer:
        return

    expenses.pop(index)

    save_expenses()

    status_label.configure(
        text="Expense deleted",
        text_color=C["orange"]
    )

    refresh_dashboard()


def edit_expense(index):
    if index >= len(expenses):
        return

    expense = expenses[index]

    window = ctk.CTkToplevel(app)
    window.title("Edit Expense")
    window.geometry("410x500")
    window.resizable(False, False)
    window.configure(
        fg_color=C["bg"]
    )

    window.transient(app)
    window.grab_set()

    ctk.CTkLabel(
        window,
        text="Edit Expense",
        text_color=C["text"],
        font=ctk.CTkFont(
            size=21,
            weight="bold"
        )
    ).pack(
        pady=(25, 15)
    )

    amount = ctk.CTkEntry(
        window,
        height=40,
        fg_color=C["input"],
        border_color=C["border2"],
        text_color=C["text"],
        placeholder_text_color=C["muted"],
        placeholder_text="Amount"
    )

    amount.pack(
        fill="x",
        padx=30,
        pady=6
    )

    amount.insert(
        0,
        str(expense.get("amount", ""))
    )

    category = ctk.CTkComboBox(
        window,
        values=get_all_categories(),
        state="normal",
        height=40,
        fg_color=C["input"],
        border_color=C["border2"],
        text_color=C["text"],
        button_color=C["blue_dark"],
        button_hover_color=C["blue_hover"]
    )

    category.pack(
        fill="x",
        padx=30,
        pady=6
    )

    category.set(
        expense.get("category", "Other")
    )

    note = ctk.CTkEntry(
        window,
        height=40,
        fg_color=C["input"],
        border_color=C["border2"],
        text_color=C["text"],
        placeholder_text_color=C["muted"],
        placeholder_text="Description"
    )

    note.pack(
        fill="x",
        padx=30,
        pady=6
    )

    note.insert(
        0,
        expense.get("note", "")
    )

    payment = ctk.CTkComboBox(
        window,
        values=payment_methods,
        height=40,
        fg_color=C["input"],
        border_color=C["border2"],
        text_color=C["text"],
        button_color=C["blue_dark"],
        button_hover_color=C["blue_hover"]
    )

    payment.pack(
        fill="x",
        padx=30,
        pady=6
    )

    payment.set(
        expense.get("payment", "Cash")
    )

    error = ctk.CTkLabel(
        window,
        text="",
        text_color=C["red"]
    )

    error.pack(
        pady=5
    )

    def save_edit():
        try:
            new_amount = float(
                amount.get().strip()
            )

        except ValueError:
            error.configure(
                text="Enter a valid amount"
            )
            return

        new_category = category.get().strip()

        if new_amount <= 0:
            error.configure(
                text="Amount must be greater than 0"
            )
            return

        if not new_category:
            error.configure(
                text="Enter a category"
            )
            return

        expenses[index]["amount"] = new_amount
        expenses[index]["category"] = new_category
        expenses[index]["note"] = note.get().strip()
        expenses[index]["payment"] = payment.get()

        save_expenses()

        window.destroy()

        refresh_dashboard()

        status_label.configure(
            text="Expense updated successfully ✓",
            text_color=C["green"]
        )

    ctk.CTkButton(
        window,
        text="Save Changes",
        height=42,
        corner_radius=10,
        command=save_edit
    ).pack(
        fill="x",
        padx=30,
        pady=(15, 7)
    )

    ctk.CTkButton(
        window,
        text="Cancel",
        height=38,
        corner_radius=10,
        fg_color=C["blue_dark"],
        hover_color=C["blue_hover"],
        text_color=C["blue"],
        command=window.destroy
    ).pack(
        fill="x",
        padx=30
    )


def create_expense_card(index, expense):
    card = ctk.CTkFrame(
        expense_list,
        corner_radius=13,
        fg_color=C["card"],
        border_width=1,
        border_color=C["border"]
    )

    card.pack(
        fill="x",
        pady=4
    )

    icon = ctk.CTkFrame(
        card,
        width=42,
        height=42,
        corner_radius=11,
        fg_color=C["blue_dark"]
    )

    icon.pack(
        side="left",
        padx=(10, 8),
        pady=9
    )

    icon.pack_propagate(False)

    ctk.CTkLabel(
        icon,
        text=category_icon(
            expense.get("category", "Other")
        ),
        font=ctk.CTkFont(size=17)
    ).pack(
        expand=True
    )

    details = ctk.CTkFrame(
        card,
        fg_color="transparent"
    )

    details.pack(
        side="left",
        fill="x",
        expand=True,
        pady=7
    )

    ctk.CTkLabel(
        details,
        text=expense.get("category", "Other"),
        text_color=C["text"],
        font=ctk.CTkFont(
            size=13,
            weight="bold"
        )
    ).pack(
        anchor="w"
    )

    note = expense.get("note", "")

    ctk.CTkLabel(
        details,
        text=note if note else "No description",
        text_color=C["muted"],
        font=ctk.CTkFont(size=10)
    ).pack(
        anchor="w"
    )

    ctk.CTkLabel(
        details,
        text=format_date_time(expense),
        text_color=C["dim"],
        font=ctk.CTkFont(size=8)
    ).pack(
        anchor="w"
    )

    ctk.CTkButton(
        card,
        text="×",
        width=28,
        height=25,
        corner_radius=6,
        fg_color=C["blue_dark"],
        hover_color=C["blue_hover"],
        text_color=C["red"],
        command=lambda i=index: delete_expense(i)
    ).pack(
        side="right",
        padx=(2, 7)
    )

    ctk.CTkButton(
        card,
        text="Edit",
        width=45,
        height=25,
        corner_radius=6,
        fg_color=C["blue_dark"],
        hover_color=C["blue_hover"],
        text_color=C["blue"],
        font=ctk.CTkFont(size=9),
        command=lambda i=index: edit_expense(i)
    ).pack(
        side="right",
        padx=2
    )

    ctk.CTkLabel(
        card,
        text=expense.get("payment", "Cash").upper(),
        width=50,
        height=20,
        corner_radius=6,
        fg_color=C["blue_dark"],
        text_color=C["blue"],
        font=ctk.CTkFont(
            size=7,
            weight="bold"
        )
    ).pack(
        side="right",
        padx=4
    )

    ctk.CTkLabel(
        card,
        text=f"-Rs. {float(expense.get('amount', 0)):,.2f}",
        text_color=C["red"],
        font=ctk.CTkFont(
            size=12,
            weight="bold"
        )
    ).pack(
        side="right",
        padx=4
    )


def refresh_expenses():
    for widget in expense_list.winfo_children():
        widget.destroy()

    if not expenses:
        ctk.CTkLabel(
            expense_list,
            text="No expenses yet\nAdd your first expense above",
            text_color=C["muted"],
            font=ctk.CTkFont(size=12)
        ).pack(
            pady=35
        )
        return

    indexes = list(
        range(len(expenses))
    )

    indexes = indexes[-8:]
    indexes.reverse()

    for index in indexes:
        create_expense_card(
            index,
            expenses[index]
        )


def refresh_categories():
    for widget in category_container.winfo_children():
        widget.destroy()

    categories = get_all_categories()

    visible = [
        category
        for category in categories
        if get_category_total(category) > 0
    ]

    if not visible:
        ctk.CTkLabel(
            category_container,
            text="No spending data yet",
            text_color=C["muted"],
            font=ctk.CTkFont(size=10)
        ).pack(
            pady=15
        )
        return

    maximum = max(
        get_category_total(category)
        for category in visible
    )

    for category in visible:
        total = get_category_total(category)

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
            text=f"{category_icon(category)} {category}",
            width=105,
            anchor="w",
            text_color=C["text"],
            font=ctk.CTkFont(size=9)
        ).pack(
            side="left"
        )

        bar = ctk.CTkFrame(
            row,
            height=8,
            corner_radius=5,
            fg_color=C["border"]
        )

        bar.pack(
            side="left",
            fill="x",
            expand=True,
            padx=5
        )

        bar.pack_propagate(False)

        width = max(
            5,
            int(100 * total / maximum)
        )

        ctk.CTkFrame(
            bar,
            width=width,
            height=8,
            corner_radius=5,
            fg_color=C["blue"]
        ).pack(
            side="left",
            fill="y"
        )

        ctk.CTkLabel(
            row,
            text=f"Rs. {total:,.0f}",
            width=65,
            anchor="e",
            text_color=C["text"],
            font=ctk.CTkFont(
                size=8,
                weight="bold"
            )
        ).pack(
            side="right"
        )


def refresh_budget_progress():
    spent = get_monthly_spent()

    if monthly_budget <= 0:
        percentage = 0
    else:
        percentage = (
            spent / monthly_budget
        ) * 100

    percentage = min(
        max(percentage, 0),
        100
    )

    budget_progress.set(
        percentage / 100
    )

    budget_percentage.configure(
        text=f"{percentage:.0f}% used"
    )

    budget_value_label.configure(
        text=f"Monthly budget: Rs. {monthly_budget:,.2f}"
    )


def refresh_dashboard():
    total = get_total_spent()
    monthly = get_monthly_spent()
    left = get_budget_left()

    total_spent_label.configure(
        text=f"Rs. {total:,.2f}"
    )

    monthly_label.configure(
        text=f"Rs. {monthly:,.2f}"
    )

    budget_label.configure(
        text=(
            f"Rs. {left:,.2f}"
            if left >= 0
            else f"-Rs. {abs(left):,.2f}"
        ),
        text_color=C["green"] if left >= 0 else C["red"]
    )

    refresh_budget_progress()
    refresh_expenses()
    refresh_categories()


def update_responsive_layout(event=None):
    global mobile_layout

    width = app.winfo_width()

    new_mobile_layout = width < 900

    if new_mobile_layout == mobile_layout:
        return

    mobile_layout = new_mobile_layout

    if mobile_layout:
        summary.pack_configure(
            padx=25
        )

        content.pack_configure(
            padx=25
        )

        left_panel.pack_forget()
        right_panel.pack_forget()

        left_panel.pack(
            fill="x",
            expand=False,
            pady=(0, 8)
        )

        right_panel.pack(
            fill="x",
            expand=False,
            pady=(8, 0)
        )

        right_panel.configure(
            height=330
        )

    else:
        summary.pack_configure(
            padx=85
        )

        content.pack_configure(
            padx=85
        )

        left_panel.pack_forget()
        right_panel.pack_forget()

        left_panel.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 7)
        )

        right_panel.pack(
            side="right",
            fill="y",
            padx=(7, 0)
        )

        right_panel.configure(
            width=285
        )


load_settings()
load_expenses()


# Header

header = ctk.CTkFrame(
    app,
    fg_color="transparent"
)

header.pack(
    fill="x",
    padx=35,
    pady=(22, 8)
)


brand = ctk.CTkFrame(
    header,
    fg_color="transparent"
)

brand.pack(
    side="left"
)


ctk.CTkLabel(
    brand,
    text="◈",
    text_color=C["blue"],
    font=ctk.CTkFont(
        size=29,
        weight="bold"
    )
).pack(
    side="left",
    padx=(0, 8)
)


brand_text = ctk.CTkFrame(
    brand,
    fg_color="transparent"
)

brand_text.pack(
    side="left"
)


ctk.CTkLabel(
    brand_text,
    text="BudgetAnalyzer",
    text_color=C["text"],
    font=ctk.CTkFont(
        size=22,
        weight="bold"
    )
).pack(
    anchor="w"
)


ctk.CTkLabel(
    brand_text,
    text="PERSONAL EXPENSE TRACKER",
    text_color=C["muted"],
    font=ctk.CTkFont(
        size=9,
        weight="bold"
    )
).pack(
    anchor="w"
)


header_buttons = ctk.CTkFrame(
    header,
    fg_color="transparent"
)

header_buttons.pack(
    side="right"
)


clear_button = ctk.CTkButton(
    header_buttons,
    text="Clear All",
    width=85,
    height=32,
    corner_radius=8,
    fg_color=C["blue_dark"],
    hover_color=C["blue_hover"],
    text_color=C["red"],
    font=ctk.CTkFont(
        size=9,
        weight="bold"
    ),
    command=clear_all
)

clear_button.pack(
    side="left",
    padx=4
)


# Month

month_header = ctk.CTkFrame(
    app,
    fg_color="transparent"
)

month_header.pack(
    fill="x",
    padx=85,
    pady=(8, 6)
)


ctk.CTkLabel(
    month_header,
    text="Expenses · " + datetime.now().strftime("%B %Y"),
    text_color=C["text"],
    font=ctk.CTkFont(
        size=17,
        weight="bold"
    )
).pack(
    side="left"
)


# Summary

summary = ctk.CTkFrame(
    app,
    fg_color="transparent"
)

summary.pack(
    fill="x",
    padx=85,
    pady=4
)


def create_summary_card(title, value):
    card = ctk.CTkFrame(
        summary,
        height=92,
        corner_radius=13,
        fg_color=C["card"],
        border_width=1,
        border_color=C["border"]
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
        text_color=C["muted"],
        font=ctk.CTkFont(
            size=9,
            weight="bold"
        )
    ).pack(
        anchor="w",
        padx=14,
        pady=(11, 3)
    )

    value_label = ctk.CTkLabel(
        card,
        text=value,
        text_color=C["text"],
        font=ctk.CTkFont(
            size=17,
            weight="bold"
        )
    )

    value_label.pack(
        anchor="w",
        padx=14
    )

    return value_label


total_spent_label = create_summary_card(
    "TOTAL SPENT",
    "Rs. 0.00"
)


# Budget card

budget_card = ctk.CTkFrame(
    summary,
    height=92,
    corner_radius=13,
    fg_color=C["card"],
    border_width=1,
    border_color=C["border"],
    cursor="hand2"
)

budget_card.pack(
    side="left",
    fill="both",
    expand=True,
    padx=4
)

budget_card.pack_propagate(False)


ctk.CTkLabel(
    budget_card,
    text="BUDGET LEFT",
    text_color=C["muted"],
    font=ctk.CTkFont(
        size=9,
        weight="bold"
    )
).pack(
    anchor="w",
    padx=14,
    pady=(10, 1)
)


budget_label = ctk.CTkLabel(
    budget_card,
    text="Rs. 50,000.00",
    text_color=C["green"],
    font=ctk.CTkFont(
        size=17,
        weight="bold"
    ),
    cursor="hand2"
)

budget_label.pack(
    anchor="w",
    padx=14
)


budget_hint = ctk.CTkLabel(
    budget_card,
    text="Click to edit budget",
    text_color=C["dim"],
    font=ctk.CTkFont(size=8),
    cursor="hand2"
)

budget_hint.pack(
    anchor="w",
    padx=14
)


budget_card.bind(
    "<Button-1>",
    lambda event: set_budget()
)

budget_label.bind(
    "<Button-1>",
    lambda event: set_budget()
)

budget_hint.bind(
    "<Button-1>",
    lambda event: set_budget()
)


monthly_label = create_summary_card(
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
    fg_color=C["panel"],
    border_width=1,
    border_color=C["border"]
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
    fg_color=C["panel"],
    border_width=1,
    border_color=C["border"]
)

right_panel.pack(
    side="right",
    fill="y",
    padx=(7, 0)
)

right_panel.pack_propagate(False)


# Left panel

ctk.CTkLabel(
    left_panel,
    text="Add Expense",
    text_color=C["text"],
    font=ctk.CTkFont(
        size=15,
        weight="bold"
    )
).pack(
    anchor="w",
    padx=18,
    pady=(15, 7)
)


amount_entry = ctk.CTkEntry(
    left_panel,
    placeholder_text="Amount (Rs.)",
    height=37,
    corner_radius=9,
    fg_color=C["input"],
    border_color=C["border2"],
    text_color=C["text"],
    placeholder_text_color=C["muted"]
)

amount_entry.pack(
    fill="x",
    padx=18,
    pady=3
)


category_box = ctk.CTkComboBox(
    left_panel,
    values=default_categories,
    state="normal",
    height=37,
    corner_radius=9,
    fg_color=C["input"],
    border_color=C["border2"],
    text_color=C["text"],
    button_color=C["blue_dark"],
    button_hover_color=C["blue_hover"]
)

category_box.pack(
    fill="x",
    padx=18,
    pady=3
)

category_box.set("Food")


note_entry = ctk.CTkEntry(
    left_panel,
    placeholder_text="Description",
    height=37,
    corner_radius=9,
    fg_color=C["input"],
    border_color=C["border2"],
    text_color=C["text"],
    placeholder_text_color=C["muted"]
)

note_entry.pack(
    fill="x",
    padx=18,
    pady=3
)


payment_box = ctk.CTkComboBox(
    left_panel,
    values=payment_methods,
    height=37,
    corner_radius=9,
    fg_color=C["input"],
    border_color=C["border2"],
    text_color=C["text"],
    button_color=C["blue_dark"],
    button_hover_color=C["blue_hover"]
)

payment_box.pack(
    fill="x",
    padx=18,
    pady=3
)

payment_box.set("Cash")


button_row = ctk.CTkFrame(
    left_panel,
    fg_color="transparent"
)

button_row.pack(
    fill="x",
    padx=18,
    pady=(4, 8)
)


status_label = ctk.CTkLabel(
    button_row,
    text="",
    font=ctk.CTkFont(size=9)
)

status_label.pack(
    side="left"
)


ctk.CTkButton(
    button_row,
    text="+ Add Expense",
    width=125,
    height=33,
    corner_radius=9,
    font=ctk.CTkFont(
        size=11,
        weight="bold"
    ),
    command=add_expense
).pack(
    side="right"
)


ctk.CTkLabel(
    left_panel,
    text="Recent Expenses",
    text_color=C["text"],
    font=ctk.CTkFont(
        size=15,
        weight="bold"
    )
).pack(
    anchor="w",
    padx=18,
    pady=(2, 5)
)


# Fixed dark scroll area

expense_list = ctk.CTkScrollableFrame(
    left_panel,
    fg_color=C["panel"],
    border_width=0,
    scrollbar_button_color=C["border2"],
    scrollbar_button_hover_color=C["border"]
)

expense_list.pack(
    fill="both",
    expand=True,
    padx=8,
    pady=(0, 8)
)


# Right panel

ctk.CTkLabel(
    right_panel,
    text="Spending Overview",
    text_color=C["text"],
    font=ctk.CTkFont(
        size=15,
        weight="bold"
    )
).pack(
    anchor="w",
    padx=18,
    pady=(17, 3)
)


ctk.CTkLabel(
    right_panel,
    text="By category",
    text_color=C["muted"],
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
    pady=10
)


ctk.CTkFrame(
    right_panel,
    height=1,
    fg_color=C["border"]
).pack(
    fill="x",
    padx=18,
    pady=5
)


ctk.CTkLabel(
    right_panel,
    text="Monthly Budget",
    text_color=C["text"],
    font=ctk.CTkFont(
        size=13,
        weight="bold"
    )
).pack(
    anchor="w",
    padx=18,
    pady=(10, 2)
)


budget_value_label = ctk.CTkLabel(
    right_panel,
    text="Monthly budget: Rs. 50,000.00",
    text_color=C["muted"],
    font=ctk.CTkFont(size=10)
)

budget_value_label.pack(
    anchor="w",
    padx=18
)


budget_progress = ctk.CTkProgressBar(
    right_panel,
    height=8,
    corner_radius=5,
    fg_color=C["border"],
    progress_color=C["blue"]
)

budget_progress.pack(
    fill="x",
    padx=18,
    pady=(10, 3)
)

budget_progress.set(0)


budget_percentage = ctk.CTkLabel(
    right_panel,
    text="0% used",
    text_color=C["dim"],
    font=ctk.CTkFont(size=9)
)

budget_percentage.pack(
    anchor="w",
    padx=18
)


ctk.CTkButton(
    right_panel,
    text="✎ Change Budget",
    height=32,
    corner_radius=8,
    fg_color=C["blue_dark"],
    hover_color=C["blue_hover"],
    text_color=C["blue"],
    font=ctk.CTkFont(
        size=10,
        weight="bold"
    ),
    command=set_budget
).pack(
    fill="x",
    padx=18,
    pady=(8, 12)
)


ctk.CTkFrame(
    right_panel,
    height=1,
    fg_color=C["border"]
).pack(
    fill="x",
    padx=18
)


ctk.CTkLabel(
    right_panel,
    text="Quick Stats",
    text_color=C["text"],
    font=ctk.CTkFont(
        size=13,
        weight="bold"
    )
).pack(
    anchor="w",
    padx=18,
    pady=(12, 5)
)


ctk.CTkLabel(
    right_panel,
    text="💰  Track every expense\n\n"
         "📊  Understand spending\n\n"
         "✎   Edit anytime\n\n"
         "🔒  Data stays local",
    justify="left",
    text_color=C["muted"],
    font=ctk.CTkFont(size=10)
).pack(
    anchor="w",
    padx=18
)


app.bind(
    "<Configure>",
    update_responsive_layout
)


refresh_dashboard()

app.mainloop()