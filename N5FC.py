import tkinter as tk
from tkinter import ttk, messagebox
import random
import sqlite3

# this is a random comment

class FlashcardGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Flashcard Game")

        # Admin credentials
        self.admin_username = "admin"
        self.admin_password = "admin123"

        # Connect to the SQLite database (or create it if it doesn't exist)
        self.conn = sqlite3.connect('flashcards.db')
        self.create_table()

        self.current_user_type = tk.StringVar()
        self.current_user_type.set("")

        # Style configuration for a more modern look
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#4CAF50')
        self.style.configure('TLabel', background='#4CAF50', foreground='#FFF', font=('Trebuchet MS', 14))
        self.style.configure('TButton', background='#FF4081', foreground='#FFF', font=('Trebuchet MS', 14))

        # Create a frame with a modern look
        self.frame = ttk.Frame(root, style='TFrame')
        self.frame.pack(padx=20, pady=20)

        # Create a label for selecting user type
        ttk.Label(self.frame, text="Select User Type", style='TLabel').grid(row=0, column=0, columnspan=2, pady=10)

        # Create a menu for selecting user type
        self.user_type_menu = tk.StringVar()
        self.user_type_menu.set("Select User Type")
        user_type_dropdown = ttk.Combobox(self.frame, textvariable=self.user_type_menu, values=["Admin", "Pupil"], state="readonly", font=('Trebuchet MS', 14))
        user_type_dropdown.grid(row=1, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

        # Create Entry widgets for login
        self.username_entry = ttk.Entry(self.frame, font=('Trebuchet MS', 14))
        self.password_entry = ttk.Entry(self.frame, show="*", font=('Trebuchet MS', 14))

        self.username_entry.grid(row=2, column=0, pady=5, padx=5, sticky="ew")
        self.password_entry.grid(row=2, column=1, pady=5, padx=5, sticky="ew")

        # Create a button to perform login
        login_button = ttk.Button(self.frame, text="Login", command=self.perform_login)
        login_button.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")

        # Create a logout button (initially hidden)
        self.logout_button = ttk.Button(self.frame, text="Logout", command=self.perform_logout, state=tk.DISABLED)
        self.logout_button.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")

    def create_table(self):
        # Create a table to store questions if it doesn't exist
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS flashcards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL
                )
            ''')

    def perform_login(self):
        user_type = self.user_type_menu.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        if user_type == "Admin" and username == self.admin_username and password == self.admin_password:
            self.current_user_type.set("Admin")
            self.open_admin_window()
        elif user_type == "Pupil":
            self.current_user_type.set("Pupil")
            self.open_pupil_menu()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials. Please try again.")

    def perform_logout(self):
        self.current_user_type.set("")
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.user_type_menu.set("Select User Type")
        self.logout_button.config(state=tk.DISABLED)

    def open_pupil_menu(self):
        # Create a new window for the pupil menu
        pupil_menu_window = tk.Toplevel(self.root)
        pupil_menu_window.title("Pupil Menu")

        # Create buttons for each topic
        ttk.Button(pupil_menu_window, text="Cell Biology", command=lambda: self.open_flashcard_window("Cell Biology")).pack(pady=10)
        ttk.Button(pupil_menu_window, text="Multicellular Organisms", command=lambda: self.open_flashcard_window("Multicellular Organisms")).pack(pady=10)
        ttk.Button(pupil_menu_window, text="Life on Earth", command=lambda: self.open_flashcard_window("Life on Earth")).pack(pady=10)
        ttk.Button(pupil_menu_window, text="Mix All Topics", command=lambda: self.open_flashcard_window("Mix All Topics")).pack(pady=10)

    def open_flashcard_window(self, topic):
        # Create a new window for the flashcard
        flashcard_window = tk.Toplevel(self.root)
        flashcard_window.title(f"Flashcards - {topic}")

        # Retrieve flashcards for the selected topic
        flashcards = self.get_flashcards_by_topic(topic)

        # Randomly shuffle the flashcards
        random.shuffle(flashcards)

        # Create a canvas for the flashcard
        flashcard_canvas = tk.Canvas(flashcard_window, width=400, height=250, bg='#E1F5FE')
        flashcard_canvas.pack(padx=20, pady=20)

        # Display the first flashcard
        current_flashcard_index = 0
        self.display_flashcard(flashcard_canvas, flashcards, current_flashcard_index)

        # Create buttons for navigation
        ttk.Button(flashcard_window, text="Previous Card", command=lambda: self.show_previous_flashcard(flashcard_canvas, flashcards, current_flashcard_index), style='TButton').pack(side=tk.LEFT, padx=10)
        ttk.Button(flashcard_window, text="Next Card", command=lambda: self.show_next_flashcard(flashcard_canvas, flashcards, current_flashcard_index), style='TButton').pack(side=tk.LEFT, padx=10)
        ttk.Button(flashcard_window, text="Back to Menu", command=flashcard_window.destroy, style='TButton').pack(side=tk.RIGHT, padx=10)

        # Bind the click event to animate the flashcard and show the answer
        flashcard_canvas.bind("<Button-1>", lambda e: self.show_answer(flashcard_canvas, flashcards, current_flashcard_index))

    def get_flashcards_by_topic(self, topic):
        # Retrieve flashcards for the selected topic from the database
        with self.conn:
            cursor = self.conn.execute('SELECT question, answer FROM flashcards WHERE topic = ?', (topic,))
        return cursor.fetchall()

    def display_flashcard(self, canvas, flashcards, index):
        # Display the question on the flashcard
        canvas.delete("all")
        question_text = canvas.create_text(200, 125, text=flashcards[index][0], fill='#000', font=('Trebuchet MS', 14), tags="question")
        canvas.bind("<Button-1>", lambda e: self.show_answer(canvas, flashcards, index))

    def show_previous_flashcard(self, canvas, flashcards, current_index):
        # Show the previous flashcard
        if current_index > 0:
            current_index -= 1
            self.display_flashcard(canvas, flashcards, current_index)

    def show_next_flashcard(self, canvas, flashcards, current_index):
        # Show the next flashcard
        if current_index < len(flashcards) - 1:
            current_index += 1
            self.display_flashcard(canvas, flashcards, current_index)

    def show_answer(self, canvas, flashcards, current_index):
        # Animate the flashcard flip with background color transition
        canvas.itemconfig("question", text=flashcards[current_index][1])
        canvas.after(1500, lambda: self.display_flashcard(canvas, flashcards, current_index))

    def open_admin_window(self):
        # Create a new window for admin actions
        admin_window = tk.Toplevel(self.root)
        admin_window.title("Admin Panel")

        # Create buttons for admin actions
        ttk.Button(admin_window, text="Add Question", command=self.show_add_question_window).pack(pady=10)
        ttk.Button(admin_window, text="Edit/Delete Questions", command=self.show_edit_questions_window).pack(pady=10)
        ttk.Button(admin_window, text="Logout", command=self.perform_logout).pack(pady=10)

    def show_add_question_window(self):
        # Create a new window for adding a question
        add_question_window = tk.Toplevel(self.root)
        add_question_window.title("Add Question")

        # Create a dropdown for selecting the topic
        ttk.Label(add_question_window, text="Select Topic:", font=('Trebuchet MS', 14)).pack(pady=5)
        topic_dropdown = ttk.Combobox(add_question_window, values=["Cell Biology", "Multicellular Organisms", "Life on Earth"], font=('Trebuchet MS', 14))
        topic_dropdown.pack(pady=5)

        # Create entry widgets for the question and answer
        ttk.Label(add_question_window, text="Question:", font=('Trebuchet MS', 14)).pack(pady=5)
        question_entry = ttk.Entry(add_question_window, font=('Trebuchet MS', 14))
        question_entry.pack(pady=5)

        ttk.Label(add_question_window, text="Answer:", font=('Trebuchet MS', 14)).pack(pady=5)
        answer_entry = ttk.Entry(add_question_window, font=('Trebuchet MS', 14))
        answer_entry.pack(pady=5)

        # Create a button to add the question to the database
        ttk.Button(add_question_window, text="Add Question", command=lambda: self.add_new_question(topic_dropdown.get(), question_entry.get(), answer_entry.get())).pack(pady=10)

    def show_edit_questions_window(self):
        # Create a new window for editing/deleting questions
        edit_questions_window = tk.Toplevel(self.root)
        edit_questions_window.title("Edit/Delete Questions")

        # Retrieve all questions from the database
        questions = self.get_all_questions()

        # Create a treeview to display questions in a table
        tree = ttk.Treeview(edit_questions_window, columns=("Topic", "Question", "Answer"), show="headings", height=15)
        tree.heading("Topic", text="Topic")
        tree.heading("Question", text="Question")
        tree.heading("Answer", text="Answer")

        # Insert questions into the treeview
        for question in questions:
            tree.insert("", "end", values=question)

        tree.pack(padx=20, pady=20)

        # Create buttons for editing and deleting
        ttk.Button(edit_questions_window, text="Edit Selected", command=lambda: self.edit_selected_question(tree)).pack(side=tk.LEFT, padx=10)
        ttk.Button(edit_questions_window, text="Delete Selected", command=lambda: self.delete_selected_question(tree)).pack(side=tk.LEFT, padx=10)

    def get_all_questions(self):
        # Retrieve all questions from the database
        with self.conn:
            cursor = self.conn.execute('SELECT topic, question, answer FROM flashcards')
        return cursor.fetchall()

    def add_new_question(self, topic, question, answer):
        if topic and question and answer:
            with self.conn:
                self.conn.execute('''
                    INSERT INTO flashcards (topic, question, answer)
                    VALUES (?, ?, ?)
                ''', (topic, question, answer))
                messagebox.showinfo("Success", "New question added successfully!")
        else:
            messagebox.showerror("Error", "Please fill in all fields.")

    def edit_selected_question(self, tree):
        # Get the selected question from the tree
        selected_item = tree.selection()
        if selected_item:
            selected_question = tree.item(selected_item, "values")
            # Implement the editing functionality here

    def delete_selected_question(self, tree):
        # Delete the selected question from the database
        selected_item = tree.selection()
        if selected_item:
            question_id = tree.item(selected_item, "values")[0]
            with self.conn:
                self.conn.execute('DELETE FROM flashcards WHERE id = ?', (question_id,))

# Create the main window
root = tk.Tk()

# Instantiate the FlashcardGame class
flashcard_game = FlashcardGame(root)

# Run the main loop
root.mainloop()
