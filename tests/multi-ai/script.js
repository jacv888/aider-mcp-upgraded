document.addEventListener("DOMContentLoaded", () => {
  const todoInput = document.getElementById("todo-input");
  const todoList = document.getElementById("todo-list");
  const addBtn = document.getElementById("add-btn");

  // Load todos from localStorage or initialize empty array
  let todos = JSON.parse(localStorage.getItem("todos")) || [];

  // Save todos to localStorage
  const saveTodos = () => {
    localStorage.setItem("todos", JSON.stringify(todos));
  };

  // Create a todo list item element with animations and event handlers
  const createTodoElement = (todo) => {
    const li = document.createElement("li");
    li.className = "todo-item";
    li.dataset.id = todo.id;

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = todo.completed;
    checkbox.className = "todo-checkbox";

    const span = document.createElement("span");
    span.textContent = todo.text;
    span.className = "todo-text";
    if (todo.completed) {
      span.classList.add("completed");
    }

    const deleteBtn = document.createElement("button");
    deleteBtn.textContent = "✕";
    deleteBtn.className = "delete-btn";

    // Toggle complete on checkbox change
    checkbox.addEventListener("change", () => {
      todo.completed = checkbox.checked;
      if (todo.completed) {
        span.classList.add("completed");
      } else {
        span.classList.remove("completed");
      }
      saveTodos();
    });

    // Delete todo with fade out animation
    deleteBtn.addEventListener("click", () => {
      li.classList.add("fade-out");
      li.addEventListener("animationend", () => {
        todos = todos.filter((t) => t.id !== todo.id);
        saveTodos();
        li.remove();
      });
    });

    li.appendChild(checkbox);
    li.appendChild(span);
    li.appendChild(deleteBtn);

    return li;
  };

  // Render all todos
  const renderTodos = () => {
    todoList.innerHTML = "";
    todos.forEach((todo) => {
      const todoElement = createTodoElement(todo);
      todoList.appendChild(todoElement);
    });
  };

  // Add new todo
  const addTodo = () => {
    const text = todoInput.value.trim();
    if (!text) return;
    const newTodo = {
      id: Date.now(),
      text,
      completed: false,
    };
    todos.push(newTodo);
    saveTodos();
    const todoElement = createTodoElement(newTodo);
    todoList.appendChild(todoElement);
    todoInput.value = "";
    todoInput.focus();
  };

  // Event listeners
  addBtn.addEventListener("click", addTodo);
  todoInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      addTodo();
    }
  });

  // Initial render
  renderTodos();
});
