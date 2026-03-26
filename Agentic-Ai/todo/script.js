document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('todo-input');
    const addBtn = document.getElementById('add-btn');
    const todoList = document.getElementById('todo-list');

    addBtn.addEventListener('click', () => {
        const task = input.value.trim();
        if (task) {
            addTask(task);
            input.value = '';
        }
    });

    function addTask(text) {
        const li = document.createElement('li');
        li.innerHTML = `
            <span>${text}</span>
            <button class="delete-btn">Delete</button>
        `;
        
        li.querySelector('.delete-btn').addEventListener('click', () => {
            li.remove();
        });

        todoList.appendChild(li);
    }
});