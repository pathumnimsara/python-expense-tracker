import customtkinter as ctk
import json


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


app = ctk.CTk()
app.title("ExpenseFlow")
app.geometry("950x760")
app.resizable(False, False)


expenses = []
total_spent = 0.0
FILE_NAME = "expenses.json"

category_totals = {
    "Food": 0.0,
    "Transport": 0.0,
    "Education": 0.0,
    "Shopping": 0.0,
    "Other": 0.0
}


def save_expenses():
    with open(FILE_NAME, "w") as file:
        json.dump(expenses, file, indent=4)


def update_category_summary():
    for category in category_totals:
        category_labels[category].configure(
            text=f"{category}\nRs. {category_totals[category]:,.2f}"
        )


def display_expense(expense):
    amount = expense["amount"]
    category = expense["category"]
    note = expense["note"]

    expense_card = ctk.CTkFrame(
        expense_list_frame,
        corner_radius=12,
        fg_color=("#F3F4F6", "#20242B")
    )

    expense_card.pack(
        fill="x",
        pady=5
    )

    left_frame = ctk.CTkFrame(
        expense_card,
        fg_color="transparent"
    )
    left_frame.pack(
        side="left",
        fill="x",
        expand=True,
        padx=15,
        pady=12
    )

    category_label = ctk.CTkLabel(
        left_frame,
        text=category,
        font=ctk.CTkFont(
            size=15,
            weight="bold"
        )
    )

    category_label.pack(
        anchor="w"
    )

    note_label = ctk.CTkLabel(
        left_frame,
        text=note if note else "No description",
        font=ctk.CTkFont(size=12),
        text_color=("gray40", "gray70")
    )

    note_label.pack(
        anchor="w",
        pady=(3, 0)
    )

    amount_label = ctk.CTkLabel(
        expense_card,
        text=f"Rs. {amount:,.2f}",
        font=ctk.CTkFont(
            size=15,
            weight="bold"
        )
    )

    amount_label.pack(
        side="right",
        padx=20
    )


def load_expenses():
    global total_spent

    try:
        with open(FILE_NAME, "r") as file:
            saved_expenses = json.load(file)

        for expense in saved_expenses:
            expenses.append(expense)

            amount = expense["amount"]
            category = expense["category"]

            total_spent += amount

            if category in category_totals:
                category_totals[category] += amount

            display_expense(expense)

        total_label.configure(
            text=f"Rs. {total_spent:,.2f}"
        )

        month_label.configure(
            text=f"Rs. {total_spent:,.2f}"
        )

        update_category_summary()

    except FileNotFoundError:
        empty_label.pack(
            pady=40
        )


def add_expense():
    global total_spent

    amount_text = amount_entry.get().strip()
    category = category_box.get()
    note = note_entry.get().strip()

    if not amount_text:
        return

    try:
        amount = float(amount_text)
    except ValueError:
        return

    if amount <= 0:
        return

    expense = {
        "amount": amount,
        "category": category,
        "note": note
    }

    expenses.append(expense)

    total_spent += amount

    if category in category_totals:
        category_totals[category] += amount

    empty_label.pack_forget()

    display_expense(expense)

    total_label.configure(
        text=f"Rs. {total_spent:,.2f}"
    )

    month_label.configure(
        text=f"Rs. {total_spent:,.2f}"
    )

    update_category_summary()

    save_expenses()

    amount_entry.delete(
        0,
        "end"
    )

    note_entry.delete(
        0,
        "end"
    )


header = ctk.CTkFrame(
    app,
    fg_color="transparent"
)

header.pack(
    fill="x",
    padx=35,
    pady=(28, 15)
)


header_left = ctk.CTkFrame(
    header,
    fg_color="transparent"
)

header_left.pack(
    side="left"
)


title = ctk.CTkLabel(
    header_left,
    text="💰  ExpenseFlow",
    font=ctk.CTkFont(
        size=30,
        weight="bold"
    )
)

title.pack(
    anchor="w"
)


subtitle = ctk.CTkLabel(
    header_left,
    text="Smart way to manage your daily expenses",
    font=ctk.CTkFont(size=13),
    text_color=("gray40", "gray70")
)

subtitle.pack(
    anchor="w",
    pady=(3, 0)
)


summary = ctk.CTkFrame(
    app,
    fg_color="transparent"
)

summary.pack(
    fill="x",
    padx=35,
    pady=5
)


total_card = ctk.CTkFrame(
    summary,
    corner_radius=18,
    fg_color=("#E8F1FF", "#17263A")
)

total_card.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(0, 8)
)


ctk.CTkLabel(
    total_card,
    text="TOTAL SPENT",
    font=ctk.CTkFont(
        size=12,
        weight="bold"
    ),
    text_color=("gray40", "gray70")
).pack(
    anchor="w",
    padx=22,
    pady=(17, 3)
)


total_label = ctk.CTkLabel(
    total_card,
    text="Rs. 0.00",
    font=ctk.CTkFont(
        size=27,
        weight="bold"
    )
)

total_label.pack(
    anchor="w",
    padx=22,
    pady=(0, 17)
)


month_card = ctk.CTkFrame(
    summary,
    corner_radius=18,
    fg_color=("#F1EBFF", "#28203B")
)

month_card.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(8, 0)
)


ctk.CTkLabel(
    month_card,
    text="THIS MONTH",
    font=ctk.CTkFont(
        size=12,
        weight="bold"
    ),
    text_color=("gray40", "gray70")
).pack(
    anchor="w",
    padx=22,
    pady=(17, 3)
)


month_label = ctk.CTkLabel(
    month_card,
    text="Rs. 0.00",
    font=ctk.CTkFont(
        size=27,
        weight="bold"
    )
)

month_label.pack(
    anchor="w",
    padx=22,
    pady=(0, 17)
)


form = ctk.CTkFrame(
    app,
    corner_radius=18
)

form.pack(
    fill="x",
    padx=35,
    pady=15
)


ctk.CTkLabel(
    form,
    text="Add New Expense",
    font=ctk.CTkFont(
        size=19,
        weight="bold"
    )
).pack(
    anchor="w",
    padx=22,
    pady=(17, 10)
)


amount_entry = ctk.CTkEntry(
    form,
    placeholder_text="Amount (Rs.)",
    height=42,
    corner_radius=10
)

amount_entry.pack(
    fill="x",
    padx=22,
    pady=5
)


category_box = ctk.CTkComboBox(
    form,
    values=[
        "Food",
        "Transport",
        "Education",
        "Shopping",
        "Other"
    ],
    height=42,
    corner_radius=10
)

category_box.pack(
    fill="x",
    padx=22,
    pady=5
)

category_box.set("Food")


note_entry = ctk.CTkEntry(
    form,
    placeholder_text="Description",
    height=42,
    corner_radius=10
)

note_entry.pack(
    fill="x",
    padx=22,
    pady=5
)


add_button = ctk.CTkButton(
    form,
    text="+  Add Expense",
    height=42,
    corner_radius=10,
    font=ctk.CTkFont(
        size=14,
        weight="bold"
    ),
    command=add_expense
)

add_button.pack(
    anchor="e",
    padx=22,
    pady=(7, 17)
)


category_summary = ctk.CTkFrame(
    app,
    corner_radius=18
)

category_summary.pack(
    fill="x",
    padx=35,
    pady=5
)


ctk.CTkLabel(
    category_summary,
    text="Spending by Category",
    font=ctk.CTkFont(
        size=17,
        weight="bold"
    )
).pack(
    anchor="w",
    padx=22,
    pady=(15, 8)
)


category_labels_frame = ctk.CTkFrame(
    category_summary,
    fg_color="transparent"
)

category_labels_frame.pack(
    fill="x",
    padx=15,
    pady=(0, 15)
)


category_labels = {}


for category in category_totals:

    card = ctk.CTkFrame(
        category_labels_frame,
        corner_radius=12,
        fg_color=("#F3F4F6", "#20242B")
    )

    card.pack(
        side="left",
        fill="both",
        expand=True,
        padx=5
    )

    label = ctk.CTkLabel(
        card,
        text=f"{category}\nRs. 0.00",
        font=ctk.CTkFont(
            size=12,
            weight="bold"
        )
    )

    label.pack(
        pady=10
    )

    category_labels[category] = label


recent = ctk.CTkFrame(
    app,
    corner_radius=18
)

recent.pack(
    fill="both",
    expand=True,
    padx=35,
    pady=(10, 25)
)


ctk.CTkLabel(
    recent,
    text="Recent Expenses",
    font=ctk.CTkFont(
        size=19,
        weight="bold"
    )
).pack(
    anchor="w",
    padx=22,
    pady=(15, 8)
)


expense_list_frame = ctk.CTkScrollableFrame(
    recent,
    fg_color="transparent"
)

expense_list_frame.pack(
    fill="both",
    expand=True,
    padx=12,
    pady=(0, 12)
)


empty_label = ctk.CTkLabel(
    expense_list_frame,
    text="No expenses yet.\nAdd your first expense above.",
    font=ctk.CTkFont(size=13),
    text_color=("gray45", "gray65")
)


load_expenses()

if not expenses:
    empty_label.pack(
        pady=40
    )


app.mainloop()