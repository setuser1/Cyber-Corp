#ai generated
#version 3
#added a GUI, shuffled questions, and an option to add multiple questions
#tested
#when you save a file using this program it will actually create a file on your device and save it there
#you can access your quiz files any time using this progran as long as you don't delete it and is using the same device

#ideas that might possibly be added
#timed questions and math symbols for certain quizzes

import os
import random
import tkinter as tk
from tkinter import messagebox, simpledialog
import tkinter.font as tkFont

# Helper function: Recursively set the width, ipady, and font size of widgets in a container.
def scale_entries_and_fonts(container):
    new_width = max(20, container.winfo_width() // 15)
    new_ipady = max(5, container.winfo_height() // 30)
    new_font_size = max(8, container.winfo_width() // 50)
    for child in container.winfo_children():
        if isinstance(child, tk.Entry):
            child.config(width=new_width)
            try:
                child.pack_configure(ipady=new_ipady, padx=10)
            except Exception:
                pass
        try:
            current_font = tkFont.Font(font=child.cget("font"))
            current_font.configure(size=new_font_size)
            child.config(font=current_font)
        except Exception:
            pass
        scale_entries_and_fonts(child)

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz Program")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        
        self.quiz = []  # Holds quiz questions
        self.selected_file = None

        # Main Menu Interface
        self.main_label = tk.Label(root, text="Select a quiz option:", font=("Arial", 14))
        self.main_label.pack(pady=10, fill=tk.X, expand=True, padx=10)

        self.list_button = tk.Button(root, text="Show Available Quizzes", command=self.list_quizzes)
        self.list_button.pack(pady=5, fill=tk.X, expand=True, padx=10)

        self.new_button = tk.Button(root, text="Create New Quiz", command=self.create_quiz_gui)
        self.new_button.pack(pady=5, fill=tk.X, expand=True, padx=10)

        self.delete_button = tk.Button(root, text="Delete a Quiz", command=self.delete_quiz_gui)
        self.delete_button.pack(pady=5, fill=tk.X, expand=True, padx=10)
    
    # ---------- Helper Methods ----------
    def _select_quiz(self, filename):
        if hasattr(self, "list_window") and self.list_window.winfo_exists():
            self.list_window.destroy()
        self.quiz_options(filename)
    
    def _close_and_run(self, window, func):
        window.destroy()
        func()
    
    # ---------- Listing & Deleting Files ----------
    def list_quizzes(self):
        quiz_files = [f for f in os.listdir() if f.endswith((".quiz", ".txt", ".csv", ".json"))]
        if quiz_files:
            self.list_window = tk.Toplevel(self.root)
            self.list_window.title("Available Quizzes")
            self.list_window.bind("<Configure>", lambda event: scale_entries_and_fonts(self.list_window))
            tk.Label(self.list_window, text="Select a quiz:", font=("Arial", 12))\
                .pack(pady=5, fill=tk.X, expand=True, padx=10)
            for filename in quiz_files:
                btn = tk.Button(self.list_window, text=filename,
                                command=lambda f=filename: self._select_quiz(f))
                btn.pack(pady=2, fill=tk.X, expand=True, padx=10)
        else:
            messagebox.showinfo("No Quizzes Found", "No quiz files available.")
    
    def delete_quiz_gui(self):
        quiz_files = [f for f in os.listdir() if f.endswith((".quiz", ".txt", ".csv", ".json"))]
        if quiz_files:
            self.delete_window = tk.Toplevel(self.root)
            self.delete_window.title("Delete a Quiz")
            self.delete_window.bind("<Configure>", lambda event: scale_entries_and_fonts(self.delete_window))
            tk.Label(self.delete_window, text="Select a quiz to delete:", font=("Arial", 12))\
                .pack(pady=5, fill=tk.X, expand=True, padx=10)
            for filename in quiz_files:
                btn = tk.Button(self.delete_window, text=filename,
                                command=lambda f=filename: self.confirm_delete(f))
                btn.pack(pady=2, fill=tk.X, expand=True, padx=10)
        else:
            messagebox.showinfo("No Quizzes Found", "No quiz files available to delete.")
    
    def confirm_delete(self, filename):
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{filename}'?"):
            try:
                os.remove(filename)
                messagebox.showinfo("Deleted", f"'{filename}' has been deleted.")
                self.delete_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete '{filename}': {e}")
    
    # ---------- Quiz Options ----------
    def quiz_options(self, filename):
        self.selected_file = filename
        self.quiz = self.load_quiz(filename)
        options_window = tk.Toplevel(self.root)
        options_window.title("Quiz Options")
        options_window.bind("<Configure>", lambda event: scale_entries_and_fonts(options_window))
        tk.Label(options_window, text=f"Selected quiz: {filename}", font=("Arial", 12))\
            .pack(pady=5, fill=tk.X, expand=True, padx=10)
        
        add_button = tk.Button(options_window, text="Add Questions",
                               command=lambda: self._close_and_run(options_window, lambda: self.add_questions_gui(filename)))
        add_button.pack(pady=5, fill=tk.X, expand=True, padx=10)
        
        start_button = tk.Button(options_window, text="Start Quiz",
                                 command=lambda: self._close_and_run(options_window, self.run_quiz_gui))
        start_button.pack(pady=5, fill=tk.X, expand=True, padx=10)
    
    # ---------- Adding Questions Screen ----------
    def add_questions_gui(self, filename):
        self.new_questions = []
        self.add_window = tk.Toplevel(self.root)
        self.add_window.title("Add Questions to Quiz")
        self.add_window.bind("<Configure>", lambda event: scale_entries_and_fonts(self.add_window))
        
        tk.Label(self.add_window, text="Select question type:", font=("Arial", 12))\
            .pack(pady=5, fill=tk.X, expand=True, padx=10)
        self.add_qtype = tk.StringVar(value="FR")
        frame = tk.Frame(self.add_window)
        frame.pack(pady=2, fill=tk.X, expand=True, padx=10)
        tk.Radiobutton(frame, text="Free Response", variable=self.add_qtype, value="FR",
                       command=self.updateAddQuestionFields).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(frame, text="Multiple Choice", variable=self.add_qtype, value="MC",
                       command=self.updateAddQuestionFields).pack(side=tk.LEFT, padx=5)
        
        tk.Label(self.add_window, text="Enter Question:")\
            .pack(fill=tk.X, expand=True, padx=10)
        self.add_question_entry = tk.Entry(self.add_window, width=50)
        self.add_question_entry.pack(pady=2, fill=tk.X, expand=True, padx=10)
        
        # FR answer fields.
        self.fr_answer_label = tk.Label(self.add_window, text="Free Response Answer (for FR questions):")
        self.fr_answer_entry = tk.Entry(self.add_window, width=50)
        
        # MC dynamic fields.
        self.mc_dynamic_frame_add = None  
        self.mc_choices_container_add = None
        self.mc_radio_frame_add = None
        self.mc_choice_entries_add = []
        self.mc_correct_var_add = None
        
        self.updateAddQuestionFields()
        
        bottom_frame = tk.Frame(self.add_window)
        bottom_frame.pack(side=tk.BOTTOM, pady=10, fill=tk.X, expand=True, padx=10)
        self.add_q_button = tk.Button(bottom_frame, text="Add Question", command=self.add_question_existing)
        self.save_added_button = tk.Button(bottom_frame, text="Save Added Questions",
                                           command=lambda: self.save_new_questions(filename))
        self.add_q_button.grid(row=0, column=0, padx=10, sticky="ew")
        self.save_added_button.grid(row=0, column=1, padx=10, sticky="ew")
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=1)
    
    def updateAddQuestionFields(self):
        qtype = self.add_qtype.get()
        self.fr_answer_label.pack_forget()
        self.fr_answer_entry.pack_forget()
        if self.mc_dynamic_frame_add:
            self.mc_dynamic_frame_add.destroy()
            self.mc_choices_container_add.destroy()
            self.mc_radio_frame_add.destroy()
        
        if qtype == "FR":
            self.fr_answer_label.pack(fill=tk.X, expand=True, padx=10)
            self.fr_answer_entry.pack(pady=2, fill=tk.X, expand=True, padx=10)
        elif qtype == "MC":
            self.mc_dynamic_frame_add = tk.Frame(self.add_window)
            self.mc_dynamic_frame_add.pack(pady=5, fill=tk.X, expand=True, padx=10)
            tk.Label(self.mc_dynamic_frame_add, text="Number of choices:").pack(side=tk.LEFT)
            self.mc_num_choices_var = tk.StringVar(value="4")
            self.mc_num_choices_spinbox = tk.Spinbox(self.mc_dynamic_frame_add, from_=2, to=10, width=5,
                                                     textvariable=self.mc_num_choices_var)
            self.mc_num_choices_spinbox.pack(side=tk.LEFT, padx=5)
            self.mc_generate_button_add = tk.Button(self.mc_dynamic_frame_add, text="Generate Options",
                                                    command=self.generateMCFieldsAdd)
            self.mc_generate_button_add.pack(side=tk.LEFT, padx=5)
            
            self.mc_choices_container_add = tk.Frame(self.add_window)
            self.mc_choices_container_add.pack(pady=5, fill=tk.X, expand=True, padx=10)
            self.mc_radio_frame_add = tk.Frame(self.add_window)
            self.mc_radio_frame_add.pack(pady=5, fill=tk.X, expand=True, padx=10)
    
def generateMCFieldsAdd(self):
    # Clear all existing widgets in the choice containers
    if self.mc_choices_container_add:
        for widget in self.mc_choices_container_add.winfo_children():
            widget.destroy()
    if self.mc_radio_frame_add:
        for widget in self.mc_radio_frame_add.winfo_children():
            widget.destroy()
    
    try:
        # Get the number of choices from the spinbox
        num = int(self.mc_num_choices_var.get())
    except ValueError:
        messagebox.showwarning("Input Error", "Please enter a valid number for choices.")
        return
    
    # Regenerate the fields for multiple-choice options
    self.mc_choice_entries_add = []
    for i in range(num):
        entry = tk.Entry(self.mc_choices_container_add, width=50)
        entry.pack(pady=2, fill=tk.X, expand=True, padx=10)
        self.mc_choice_entries_add.append(entry)
    
    # Regenerate the radio buttons for selecting the correct answer
    self.mc_correct_var_add = tk.IntVar(value=0)
    tk.Label(self.mc_radio_frame_add, text="Select correct answer:").pack(side=tk.LEFT)
    for i in range(num):
        rb = tk.Radiobutton(self.mc_radio_frame_add, text=f"Option {i+1}",
                            variable=self.mc_correct_var_add, value=i,
                            indicatoron=False, width=10, height=2, padx=5, pady=5)
        rb.pack(side=tk.LEFT, padx=5)
    
    def add_question_existing(self):
        qtype = self.add_qtype.get()
        question = self.add_question_entry.get().strip()
        if not question:
            messagebox.showwarning("Input Error", "Question text is required!")
            return
        if qtype == "FR":
            answer = self.fr_answer_entry.get().strip()
            if not answer:
                messagebox.showwarning("Input Error", "Answer is required for free response!")
                return
            new_q = ("FR", question, answer)
        else:
            if not hasattr(self, 'mc_choice_entries_add') or len(self.mc_choice_entries_add) == 0:
                messagebox.showwarning("Input Error", "Please generate the options fields.")
                return
            choices_list = []
            for entry in self.mc_choice_entries_add:
                t = entry.get().strip()
                if not t:
                    messagebox.showwarning("Input Error", "All choice fields must be filled.")
                    return
                choices_list.append(t)
            correct_index = self.mc_correct_var_add.get()
            if correct_index < 0 or correct_index >= len(choices_list):
                messagebox.showwarning("Input Error", "Please select a valid correct option.")
                return
            correct_answer = choices_list[correct_index]
            new_q = ("MC", question, choices_list, correct_answer)
        
        self.new_questions.append(new_q)
        self.quiz.append(new_q)
        messagebox.showinfo("Added", f"Added question: {question}")
        self.add_question_entry.delete(0, tk.END)
        if qtype == "FR":
            self.fr_answer_entry.delete(0, tk.END)
        else:
            for entry in self.mc_choice_entries_add:
                entry.delete(0, tk.END)
    
    def save_new_questions(self, filename):
        try:
            with open(filename, "a", encoding="utf-8") as file:
                for q in self.new_questions:
                    if q[0] == "FR":
                        file.write(f"FR|{q[1]}|{q[2]}\n")
                    elif q[0] == "MC":
                        choices_str = ";".join(q[2])
                        file.write(f"MC|{q[1]}|{choices_str}|{q[3]}\n")
            messagebox.showinfo("Saved", f"New questions have been added to {filename}")
            self.add_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save quiz: {e}")
    
    def create_quiz_gui(self):
        self.quiz = []
        self.new_window = tk.Toplevel(self.root)
        self.new_window.title("Create New Quiz")
        self.new_window.bind("<Configure>", lambda event: scale_entries_and_fonts(self.new_window))
        
        tk.Label(self.new_window, text="Select question type:", font=("Arial", 12))\
            .pack(pady=5, fill=tk.X, expand=True, padx=10)
        self.new_qtype = tk.StringVar(value="FR")
        frame = tk.Frame(self.new_window)
        frame.pack(pady=2, fill=tk.X, expand=True, padx=10)
        tk.Radiobutton(frame, text="Free Response", variable=self.new_qtype, value="FR",
                       command=self.updateNewQuestionFields).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(frame, text="Multiple Choice", variable=self.new_qtype, value="MC",
                       command=self.updateNewQuestionFields).pack(side=tk.LEFT, padx=5)
        
        tk.Label(self.new_window, text="Enter Question:").pack(fill=tk.X, expand=True, padx=10)
        self.question_entry_new = tk.Entry(self.new_window, width=50)
        self.question_entry_new.pack(pady=2, fill=tk.X, expand=True, padx=10)
        
        self.fr_answer_label_new = tk.Label(self.new_window, text="Answer (for FR questions):")
        self.fr_answer_entry_new = tk.Entry(self.new_window, width=50)
        
        self.mc_dynamic_frame_new = None
        self.mc_choices_container_new = None
        self.mc_radio_frame_new = None
        self.mc_choice_entries_new = []
        self.mc_correct_var_new = None
        
        self.updateNewQuestionFields()
        
        bottom_frame = tk.Frame(self.new_window)
        bottom_frame.pack(side=tk.BOTTOM, pady=10, fill=tk.X, expand=True, padx=10)
        self.add_new_button = tk.Button(bottom_frame, text="Add Question", command=self.add_question_new)
        self.save_new_button = tk.Button(bottom_frame, text="Save Quiz", command=self.save_quiz_gui_new)
        self.add_new_button.grid(row=0, column=0, padx=10, sticky="ew")
        self.save_new_button.grid(row=0, column=1, padx=10, sticky="ew")
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=1)
    
    def updateNewQuestionFields(self):
        qtype = self.new_qtype.get()
        self.fr_answer_label_new.pack_forget()
        self.fr_answer_entry_new.pack_forget()
        if self.mc_dynamic_frame_new is not None:
            self.mc_dynamic_frame_new.destroy()
            self.mc_choices_container_new.destroy()
            self.mc_radio_frame_new.destroy()
        if qtype == "FR":
            self.fr_answer_label_new.pack(fill=tk.X, expand=True, padx=10)
            self.fr_answer_entry_new.pack(pady=2, fill=tk.X, expand=True, padx=10)
        else:
            self.mc_dynamic_frame_new = tk.Frame(self.new_window)
            self.mc_dynamic_frame_new.pack(pady=5, fill=tk.X, expand=True, padx=10)
            tk.Label(self.mc_dynamic_frame_new, text="Number of choices:").pack(side=tk.LEFT)
            self.mc_num_choices_var_new = tk.StringVar(value="4")
            self.mc_num_choices_spinbox_new = tk.Spinbox(self.mc_dynamic_frame_new, from_=2, to=10, width=5,
                                                       textvariable=self.mc_num_choices_var_new)
            self.mc_num_choices_spinbox_new.pack(side=tk.LEFT, padx=5)
            self.mc_generate_button_new = tk.Button(self.mc_dynamic_frame_new, text="Generate Options", 
                                                    command=self.generateMCFieldsNew)
            self.mc_generate_button_new.pack(side=tk.LEFT, padx=5)
            self.mc_choices_container_new = tk.Frame(self.new_window)
            self.mc_choices_container_new.pack(pady=5, fill=tk.X, expand=True, padx=10)
            self.mc_radio_frame_new = tk.Frame(self.new_window)
            self.mc_radio_frame_new.pack(pady=5, fill=tk.X, expand=True, padx=10)
    
def generateMCFieldsNew(self):
    # Clear all existing widgets in the choice containers
    if self.mc_choices_container_new:
        for widget in self.mc_choices_container_new.winfo_children():
            widget.destroy()
    if self.mc_radio_frame_new:
        for widget in self.mc_radio_frame_new.winfo_children():
            widget.destroy()
    
    try:
        # Get the number of choices from the spinbox
        num = int(self.mc_num_choices_var_new.get())
    except ValueError:
        messagebox.showwarning("Input Error", "Please enter a valid number for choices.")
        return
    
    # Regenerate the fields for multiple-choice options
    self.mc_choice_entries_new = []
    for i in range(num):
        entry = tk.Entry(self.mc_choices_container_new, width=50)
        entry.pack(pady=2, fill=tk.X, expand=True, padx=10)
        self.mc_choice_entries_new.append(entry)
    
    # Regenerate the radio buttons for selecting the correct answer
    self.mc_correct_var_new = tk.IntVar(value=0)
    tk.Label(self.mc_radio_frame_new, text="Select correct answer:").pack(side=tk.LEFT)
    for i in range(num):
        rb = tk.Radiobutton(self.mc_radio_frame_new, text=f"Option {i+1}",
                            variable=self.mc_correct_var_new, value=i,
                            indicatoron=False, width=10, height=2, padx=5, pady=5)
        rb.pack(side=tk.LEFT, padx=5)
    
    def add_question_new(self):
        qtype = self.new_qtype.get()
        question = self.question_entry_new.get().strip()
        if not question:
            messagebox.showwarning("Input Error", "Question text is required!")
            return
        if qtype == "FR":
            answer = self.fr_answer_entry_new.get().strip()
            if not answer:
                messagebox.showwarning("Input Error", "Answer is required for free response!")
                return
            new_q = ("FR", question, answer)
        else:
            if not hasattr(self, 'mc_choice_entries_new') or len(self.mc_choice_entries_new) == 0:
                messagebox.showwarning("Input Error", "Please generate the options fields.")
                return
            choices_list = []
            for entry in self.mc_choice_entries_new:
                t = entry.get().strip()
                if not t:
                    messagebox.showwarning("Input Error", "All choice fields must be filled.")
                    return
                choices_list.append(t)
            correct_index = self.mc_correct_var_new.get()
            if correct_index < 0 or correct_index >= len(choices_list):
                messagebox.showwarning("Input Error", "Please select a valid correct option.")
                return
            correct_answer = choices_list[correct_index]
            new_q = ("MC", question, choices_list, correct_answer)
        
        self.quiz.append(new_q)
        messagebox.showinfo("Added", f"Added question: {question}")
        self.question_entry_new.delete(0, tk.END)
        if qtype == "FR":
            self.fr_answer_entry_new.delete(0, tk.END)
        else:
            for entry in self.mc_choice_entries_new:
                entry.delete(0, tk.END)
    
    def save_quiz_gui_new(self):
        filename = simpledialog.askstring("Quiz Name", "Enter a name for your quiz (including extension, e.g., quiz.txt):")
        if filename:
            if "." not in filename:
                filename += ".quiz"
            if os.path.exists(filename):
                if not messagebox.askyesno("File Exists", f"'{filename}' already exists. Overwrite?"):
                    return
            try:
                with open(filename, "w", encoding="utf-8") as file:
                    for q in self.quiz:
                        if q[0] == "FR":
                            file.write(f"FR|{q[1]}|{q[2]}\n")
                        elif q[0] == "MC":
                            choices_str = ";".join(q[2])
                            file.write(f"MC|{q[1]}|{choices_str}|{q[3]}\n")
                messagebox.showinfo("Saved", f"Quiz saved to {filename}")
                self.new_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save quiz: {e}")
    
    def load_quiz(self, filename):
        quiz = []
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as file:
                    lines = file.readlines()
                    for line in lines:
                        parts = line.strip().split("|")
                        if parts[0] == "FR" and len(parts) == 3:
                            quiz.append(("FR", parts[1], parts[2]))
                        elif parts[0] == "MC" and len(parts) == 4:
                            choices_list = [c.strip() for c in parts[2].split(";") if c.strip()]
                            quiz.append(("MC", parts[1], choices_list, parts[3]))
                        else:
                            messagebox.showwarning("Warning", f"Skipping invalid line: {line.strip()}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load quiz: {e}")
        return quiz
    
    # ---------- Quiz Navigation with Back and Forward Buttons ----------
    def run_quiz_gui(self):
        if not self.quiz:
            messagebox.showwarning("Error", "This quiz is empty or invalid!")
            return
        
        random.shuffle(self.quiz)
        self.user_answers = ["" for _ in range(len(self.quiz))]
        self.current_question = 0
        
        self.quiz_window = tk.Toplevel(self.root)
        self.quiz_window.title("Quiz")
        self.quiz_window.bind("<Configure>", lambda event: scale_entries_and_fonts(self.quiz_window))
        
        self.question_label = tk.Label(self.quiz_window, text="", font=("Arial", 14))
        self.question_label.pack(pady=10, fill=tk.X, expand=True, padx=10)
        
        self.answer_frame = tk.Frame(self.quiz_window)
        self.answer_frame.pack(pady=5, fill=tk.BOTH, expand=True, padx=10)
        
        self.nav_frame = tk.Frame(self.quiz_window)
        self.nav_frame.pack(pady=5, fill=tk.X, expand=True, padx=10)
        self.back_button = tk.Button(self.nav_frame, text="Back", command=self.go_back)
        self.back_button.pack(side=tk.LEFT, padx=5)
        self.next_button = tk.Button(self.nav_frame, text="Next", command=self.go_forward)
        self.next_button.pack(side=tk.RIGHT, padx=5)
        
        self.show_question()
    
    def show_question(self):
        for widget in self.answer_frame.winfo_children():
            widget.destroy()
        current = self.quiz[self.current_question]
        qtype = current[0]
        self.question_label.config(text=current[1])
        if qtype == "FR":
            self.answer_entry = tk.Entry(self.answer_frame, width=50)
            self.answer_entry.pack(fill=tk.X, expand=True, padx=10)
            if self.user_answers[self.current_question]:
                self.answer_entry.insert(0, self.user_answers[self.current_question])
        elif qtype == "MC":
            self.answer_var = tk.StringVar()
            if self.user_answers[self.current_question]:
                self.answer_var.set(self.user_answers[self.current_question])
            for choice in current[2]:
                rb = tk.Radiobutton(self.answer_frame, text=choice, variable=self.answer_var, value=choice,
                                    indicatoron=False, width=10, height=2, padx=5, pady=5)
                rb.pack(anchor="w", fill=tk.X, expand=True, padx=10)
        if self.current_question == 0:
            self.back_button.config(state=tk.DISABLED)
        else:
            self.back_button.config(state=tk.NORMAL)
        if self.current_question == len(self.quiz) - 1:
            self.next_button.config(text="Submit Quiz")
        else:
            self.next_button.config(text="Next")
    
    def go_forward(self):
        current = self.quiz[self.current_question]
        if current[0] == "FR":
            self.user_answers[self.current_question] = self.answer_entry.get().strip()
        elif current[0] == "MC":
            self.user_answers[self.current_question] = self.answer_var.get().strip()
        if self.current_question == len(self.quiz) - 1:
            self.submit_quiz()
        else:
            self.current_question += 1
            self.show_question()
    
    def go_back(self):
        current = self.quiz[self.current_question]
        if current[0] == "FR":
            self.user_answers[self.current_question] = self.answer_entry.get().strip()
        elif current[0] == "MC":
            self.user_answers[self.current_question] = self.answer_var.get().strip()
        if self.current_question > 0:
            self.current_question -= 1
            self.show_question()
    
    def submit_quiz(self):
        self.quiz_window.destroy()
        self.results = []
        self.score = 0
        for i, q in enumerate(self.quiz):
            qtype = q[0]
            correct = q[2].strip().lower() if qtype == "FR" else q[3].strip().lower()
            user = self.user_answers[i].strip().lower() if self.user_answers[i] else ""
            is_correct = (user == correct)
            if is_correct:
                self.score += 1
            self.results.append({
                "question": q[1],
                "user_answer": user,
                "correct_answer": correct,
                "correct": is_correct
            })
        self.show_results()
    
    def show_results(self):
        results_window = tk.Toplevel(self.root)
        results_window.title("Quiz Results")
        frame = tk.Frame(results_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget = tk.Text(frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        total = len(self.quiz)
        score_text = f"You scored {self.score} out of {total}\n\n"
        text_widget.insert(tk.END, score_text)
        for i, result in enumerate(self.results, start=1):
            q_text = f"Q{i}: {result['question']}\n"
            user_text = f"Your answer: {result['user_answer']}\n"
            correct_text = f"Correct answer: {result['correct_answer']}\n"
            detail = q_text + user_text + correct_text + f"Result: {'Correct' if result['correct'] else 'Incorrect'}\n\n"
            text_widget.insert(tk.END, detail)
        text_widget.config(state=tk.DISABLED)

# Run the Tkinter GUI
root = tk.Tk()
app = QuizApp(root)
root.mainloop()
