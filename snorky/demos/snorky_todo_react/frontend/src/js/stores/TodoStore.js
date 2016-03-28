'use strict';

import { Store } from 'geiger';

export default class TodoStore extends Store {

    constructor({ actions }) {

        super();
        this.todos = [];

        /*
        * Registering action handlers
        * Intentionnaly made private (just use the actions !)
        */

        this.listen(actions, 'createTodo', todo => {
            console.log(todo)
            //this.todos = this.todos.set(todo.get('id'), todo);
            //this.changed();
        });

        this.listen(actions, 'fetchTodos', todos => {
            /*for(let todo of todos) {
                this.todos = this.todos.set(todo.get('id'), todo);
            }*/
            this.todos = todos;
            this.changed();
        });

        this.listen(actions, 'deleteTodo', todo => {
            /*this.todos = this.todos.delete(todo.get('id'));
            this.changed();*/
            console.log(todo)
        });

        this.listen(actions, 'snorky', todos => {
          this.todos = todos;
          this.changed();
        });

    }

    // Public API

    getTodos() { return this.todos; }
}
