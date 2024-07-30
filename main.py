from tkinter import *
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# Database Management
class Database:
    def __init__(self):
        self.conn = sqlite3.connect('expense.db')
        self.cur = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cur.execute('''
        CREATE TABLE IF NOT EXISTS expense_record (
            id INTEGER PRIMARY KEY,
            item_name TEXT NOT NULL,
            item_price REAL NOT NULL,
            purchase_date TEXT NOT NULL
        )
        ''')

    def insertRecord(self, item_name, item_price, purchase_date):
        self.cur.execute('''
        INSERT INTO expense_record (item_name, item_price, purchase_date)
        VALUES (?, ?, ?)
        ''', (item_name, item_price, purchase_date))
        self.conn.commit()

    def fetchRecord(self):
        self.cur.execute('SELECT * FROM expense_record')
        rows = self.cur.fetchall()
        return rows

    def removeRecord(self, id):
        self.cur.execute('DELETE FROM expense_record WHERE id = ?', (id,))
        self.conn.commit()

    def updateRecord(self, id, item_name, item_price, purchase_date):
        self.cur.execute('''
        UPDATE expense_record
        SET item_name = ?, item_price = ?, purchase_date = ?
        WHERE id = ?
        ''', (item_name, item_price, purchase_date, id))
        self.conn.commit()

    def totalBalance(self):
        self.cur.execute('SELECT SUM(item_price) FROM expense_record')
        total = self.cur.fetchone()[0]
        return total if total is not None else 0

# GUI
class ExpenseTracker(Tk):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.title("Expense Tracker")
        self.geometry("600x550")
        self.selected_id = None
        self.total_budget = 0.0

        # Setup UI components
        self.setup_ui()

    def setup_ui(self):
        # Frames
        f1 = Frame(self, padx=5, pady=5)
        f1.pack(pady=5)
        f2 = Frame(self, padx=5, pady=5)
        f2.pack(pady=5)

        # Entry fields and labels
        Label(f1, text="Item Name", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5)
        self.item_name = Entry(f1, font=("Arial", 12))
        self.item_name.grid(row=0, column=1, padx=5, pady=5)

        Label(f1, text="Item Price", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5)
        self.item_price = Entry(f1, font=("Arial", 12))
        self.item_price.grid(row=1, column=1, padx=5, pady=5)

        Label(f1, text="Purchase Date", font=("Arial", 12)).grid(row=2, column=0, padx=5, pady=5)
        self.purchase_date = Entry(f1, font=("Arial", 12))
        self.purchase_date.grid(row=2, column=1, padx=5, pady=5)

        Button(f1, text="Today", command=self.set_current_date, bg='#d3d3d3', font=("Arial", 12)).grid(row=2, column=2, padx=5, pady=5)

        # Budget-related fields and buttons
        Label(f1, text="Total Budget", font=("Arial", 12)).grid(row=3, column=0, padx=5, pady=5)
        self.total_budget_entry = Entry(f1, font=("Arial", 12))
        self.total_budget_entry.grid(row=3, column=1, padx=5, pady=5)

        Button(f1, text="Set Budget", command=self.set_budget, bg='#90ee90', font=("Arial", 12)).grid(row=3, column=2, padx=5, pady=5)
        Button(f1, text="Remaining Budget", command=self.show_remaining_budget, bg='#ffa07a', font=("Arial", 12)).grid(row=4, column=1, padx=5, pady=5)

        # Action Buttons
        Label(f1, text="").grid(row=5, column=0, padx=5, pady=10) # Add an empty Label to create row=5
        button_width = 7  # Define a common width for all buttons

        Button(f1, text="Save", command=self.save_record, bg='#add8e6', font=("Arial", 12), width=button_width).place(x=10, y=200)
        Button(f1, text="Update", command=self.update_record, bg='#87cefa', font=("Arial", 12), width=button_width).place(x=120, y=200)
        Button(f1, text="Delete", command=self.delete_record, bg='#ff6347', font=("Arial", 12), width=button_width).place(x=230, y=200)
        Button(f1, text="Clear", command=self.clear_entries, bg='#ffe4b5', font=("Arial", 12), width=button_width).place(x=340, y=200)
        # Button(f1, text="Exit", command=self.quit, bg='#000000', fg='white', font=("Arial", 12), width=button_width).place(x=450, y=200)

        # Treeview
        self.tree = ttk.Treeview(f2, columns=("ID", "Item Name", "Item Price", "Purchase Date"), show='headings')
        self.tree.heading("ID", text="ID")
        self.tree.heading("Item Name", text="Item Name")
        self.tree.heading("Item Price", text="Item Price")
        self.tree.heading("Purchase Date", text="Purchase Date")
        self.tree.column("ID", width=50)
        self.tree.column("Item Name", width=150)
        self.tree.column("Item Price", width=100)
        self.tree.column("Purchase Date", width=100)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.pack(expand=True, fill='both')

        # Total Balance Label
        self.total_label = Label(f2, text="Total Balance: $0", font=("Arial", 14))
        self.total_label.pack(pady=10)

        # Populate the treeview with initial data
        self.load_records()

    def set_current_date(self):
        self.purchase_date.delete(0, END)
        self.purchase_date.insert(END, datetime.now().strftime("%Y-%m-%d"))

    def set_budget(self):
        try:
            self.total_budget = float(self.total_budget_entry.get())
            messagebox.showinfo("Budget Set", f"Total Budget set to ${self.total_budget:.2f}")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for the budget.")

    def show_remaining_budget(self):
        total_expense = self.db.totalBalance()
        remaining_budget = self.total_budget - total_expense
        messagebox.showinfo("Remaining Budget", f"Remaining Budget: ${remaining_budget:.2f}")

    def save_record(self):
        item_name = self.item_name.get()
        item_price = self.item_price.get()
        purchase_date = self.purchase_date.get()
        if item_name and item_price and purchase_date:
            try:
                item_price = float(item_price)
                self.db.insertRecord(item_name, item_price, purchase_date)
                self.load_records()
                self.clear_entries()
                if self.db.totalBalance() > self.total_budget:
                    messagebox.showwarning("Budget Exceeded", "You have exceeded your total budget!")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid price.")
        else:
            messagebox.showwarning("Input Error", "Please fill all fields.")

    def update_record(self):
        if self.selected_id is None:
            messagebox.showwarning("Selection Error", "No record selected.")
            return

        item_name = self.item_name.get()
        item_price = self.item_price.get()
        purchase_date = self.purchase_date.get()
        if item_name and item_price and purchase_date:
            try:
                item_price = float(item_price)
                self.db.updateRecord(self.selected_id, item_name, item_price, purchase_date)
                self.load_records()
                self.clear_entries()
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid price.")
        else:
            messagebox.showwarning("Input Error", "Please fill all fields.")

    def delete_record(self):
        if self.selected_id is None:
            messagebox.showwarning("Selection Error", "No record selected.")
            return
        self.db.removeRecord(self.selected_id)
        self.load_records()
        self.clear_entries()

    def load_records(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for row in self.db.fetchRecord():
            self.tree.insert('', 'end', values=row)
        self.update_total_balance()

    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item)
            values = item['values']
            self.selected_id = values[0]
            self.item_name.delete(0, END)
            self.item_name.insert(END, values[1])
            self.item_price.delete(0, END)
            self.item_price.insert(END, values[2])
            self.purchase_date.delete(0, END)
            self.purchase_date.insert(END, values[3])

    def clear_entries(self):
        self.item_name.delete(0, END)
        self.item_price.delete(0, END)
        self.purchase_date.delete(0, END)
        self.selected_id = None

    def update_total_balance(self):
        total_balance = self.db.totalBalance()
        self.total_label.config(text=f"Total Balance: ${total_balance:.2f}")

if __name__ == "__main__":
    db = Database()
    app = ExpenseTracker(db)
    app.mainloop()
