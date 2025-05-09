import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import Database

class BioInfoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Conference Bio Manager")
        self.geometry("1000x700")
        self.db = Database()
        
        self.create_widgets()
        self.load_attendees()
        
    def create_widgets(self):
        # Main Container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview for Attendees
        self.tree = ttk.Treeview(main_frame, columns=('ID', 'First Name', 'Last Name', 'Email', 'Organization'), show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('First Name', text='First Name')
        self.tree.heading('Last Name', text='Last Name')
        self.tree.heading('Email', text='Email')
        self.tree.heading('Organization', text='Organization')
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Button Panel
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Add Attendee", command=self.open_add_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Edit Attendee", command=self.open_edit_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete Attendee", command=self.delete_attendee).pack(side=tk.LEFT, padx=5)
        
        # Search
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(pady=5)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<KeyRelease>', self.search_attendees)
        
    def load_attendees(self):
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Fetch from database
        attendees = self.db.get_attendees()
        for attendee in attendees:
            self.tree.insert('', 'end', values=(
                attendee[0],  # ID
                attendee[1],  # First Name
                attendee[2],  # Last Name
                attendee[3],  # Email
                attendee[5]   # Organization
            ))
    
    def open_add_dialog(self):
        AddAttendeeDialog(self, self.db)
    
    def open_edit_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an attendee to edit")
            return
        item = self.tree.item(selected[0])
        EditAttendeeDialog(self, self.db, item['values'])
    
    def delete_attendee(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an attendee to delete")
            return
        attendee_id = self.tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this attendee?"):
            # Implement delete in database
            cursor = self.db.conn.cursor()
            cursor.execute('DELETE FROM attendees WHERE id=?', (attendee_id,))
            self.db.conn.commit()
            self.load_attendees()
    
    def search_attendees(self, event=None):
        search_term = self.search_var.get()
        # Implement search in database
        attendees = self.db.get_attendees(search_term)
        self.load_attendees(attendees)

class AddAttendeeDialog(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.title("Add New Attendee")
        self.db = db
        self.create_widgets()
        
    def create_widgets(self):
        form_frame = ttk.Frame(self)
        form_frame.pack(padx=20, pady=20)
        
        # Form Fields
        labels = ['First Name:', 'Last Name:', 'Email:', 'Phone:', 'Organization:', 'Position:', 'Bio:']
        self.entries = {}
        
        for i, label in enumerate(labels):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky='w', pady=5)
            entry = ttk.Entry(form_frame, width=40) if label != 'Bio:' else tk.Text(form_frame, width=30, height=5)
            entry.grid(row=i, column=1, pady=5)
            self.entries[label] = entry
            
        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=len(labels), columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)
        
    def save(self):
        # Data validation
        required = ['First Name:', 'Last Name:', 'Email:']
        data = []
        for label in required:
            value = self.entries[label].get().strip()
            if not value:
                messagebox.showerror("Error", f"{label[:-1]} is required")
                return
            data.append(value)
            
        # Get optional fields
        data.append(self.entries['Phone:'].get().strip())
        data.append(self.entries['Organization:'].get().strip())
        data.append(self.entries['Position:'].get().strip())
        data.append(self.entries['Bio:'].get("1.0", tk.END).strip())
        data.append(datetime.now())  # Last attended
        
        try:
            self.db.add_attendee(data)
            self.master.load_attendees()
            self.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Email must be unique")

class EditAttendeeDialog(AddAttendeeDialog):
    def __init__(self, parent, db, attendee_data):
        super().__init__(parent, db)
        self.title("Edit Attendee")
        self.attendee_id = attendee_data[0]
        self.populate_fields(attendee_data)
        
    def populate_fields(self, data):
        fields = ['First Name:', 'Last Name:', 'Email:', 'Phone:', 'Organization:', 'Position:', 'Bio:']
        for i, field in enumerate(fields):
            if field == 'Bio:':
                self.entries[field].delete("1.0", tk.END)
                self.entries[field].insert("1.0", data[6])
            else:
                self.entries[field].delete(0, tk.END)
                self.entries[field].insert(0, data[i])
                
    def save(self):
        # Similar to AddAttendeeDialog but with update logic
        pass

if __name__ == "__main__":
    app = BioInfoApp()
    app.mainloop()
