import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

# Configurar la base de datos
try:
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY, 
                        task TEXT UNIQUE, 
                        completed BOOLEAN)''')
    conn.commit()
except sqlite3.Error as e:
    messagebox.showerror("Error", f"Error al conectar con la base de datos: {e}")
    exit()

# Funciones
def add_task():
    task = entry_task.get().strip()
    if task:
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE task = ?", (task,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO tasks (task, completed) VALUES (?, ?)", (task, False))
            conn.commit()
            entry_task.delete(0, tk.END)
            load_tasks()
        else:
            messagebox.showwarning("Aviso", "La tarea ya existe en la lista.")
    else:
        messagebox.showwarning("Aviso", "La tarea no puede estar vacía.")

def load_tasks():
    listbox_tasks.delete(*listbox_tasks.get_children())
    cursor.execute("SELECT id, task, completed FROM tasks")
    for row in cursor.fetchall():
        listbox_tasks.insert("", "end", values=(row[1], "✔" if row[2] else "✗"))

def delete_task():
    try:
        selected_item = listbox_tasks.selection()[0]
        task_text = listbox_tasks.item(selected_item, "values")[0]
        confirm = messagebox.askyesno("Confirmar eliminación", f"¿Estás seguro de que deseas eliminar la tarea: '{task_text}'?")
        if confirm:
            cursor.execute("DELETE FROM tasks WHERE task = ?", (task_text,))
            conn.commit()
            load_tasks()
    except IndexError:
        messagebox.showwarning("Aviso", "Selecciona una tarea para eliminar.")

def mark_completed():
    try:
        selected_item = listbox_tasks.selection()[0]
        task_text = listbox_tasks.item(selected_item, "values")[0]
        cursor.execute("UPDATE tasks SET completed = NOT completed WHERE task = ?", (task_text,))
        conn.commit()
        load_tasks()
    except IndexError:
        messagebox.showwarning("Aviso", "Selecciona una tarea para cambiar su estado.")

# Interfaz gráfica
root = tk.Tk()
root.title("Gestor de Tareas")
root.geometry("400x400")

frame = tk.Frame(root)
frame.pack(pady=10)

entry_task = tk.Entry(frame, width=40)
entry_task.pack(side=tk.LEFT, padx=5)

btn_add = tk.Button(frame, text="Añadir", command=add_task)
btn_add.pack(side=tk.RIGHT)

# Listbox mejorado con Treeview
tree_frame = tk.Frame(root)
tree_frame.pack(pady=10)

columns = ("Tarea", "Estado")
listbox_tasks = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
listbox_tasks.heading("Tarea", text="Tarea")
listbox_tasks.heading("Estado", text="Estado")
listbox_tasks.column("Tarea", width=250)
listbox_tasks.column("Estado", width=80, anchor="center")
listbox_tasks.pack()

btn_complete = tk.Button(root, text="Marcar/Desmarcar como completada", command=mark_completed)
btn_complete.pack(fill=tk.X)

btn_delete = tk.Button(root, text="Eliminar", command=delete_task)
btn_delete.pack(fill=tk.X)

load_tasks()
root.mainloop()

# Cerrar conexión a la base de datos al cerrar
conn.close()
