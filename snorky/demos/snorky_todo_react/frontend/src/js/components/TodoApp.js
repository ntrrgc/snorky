'use strict';

import React from 'react';
import {Router} from 'director';

import TodoItem from './TodoItem';
import TodoFooter from './TodoFooter';

export default class TodoApp extends React.Component{
  static ALL_TODOS = 'all';
  static ACTIVE_TODOS = 'active';
  static COMPLETED_TODOS = 'completed';
  static ENTER_KEY = 13;

	constructor() {
		super();
    this.state = {
			nowShowing: TodoApp.ALL_TODOS,
			editing: null,
			newTodo: ''
		}
	}

  componentDidMount() {
      this.unwatchTodostore = this.props.todostore.watch(this.forceUpdate.bind(this));
      this.props.todoactions.fetchTodosAndSubscribe();
			var setState = this.setState;
			var router = Router({
				'/': setState.bind(this, {nowShowing: TodoApp.ALL_TODOS}),
				'/active': setState.bind(this, {nowShowing: TodoApp.ACTIVE_TODOS}),
				'/completed': setState.bind(this, {nowShowing: TodoApp.COMPLETED_TODOS})
			});
			router.init()
  }

  componentWillUnmount() {
    this.unwatchTodostore();
  }

	handleChange (event) {
		this.setState({newTodo: event.target.value});
	}

  handleNewTodoKeyDown (event) {
		if (event.keyCode !== TodoApp.ENTER_KEY) {
			return;
		}

		event.preventDefault();

		var val = this.state.newTodo.trim();

		if (val) {
      this.props.todoactions.createTodo(val);
      this.setState({newTodo: ''});
		}
	}

  toggleAll (event) {
    this.props.todoactions.toggleAll(event.target.checked);
	}

	toggle (todoToToggle) {
    todoToToggle.completed = !todoToToggle.completed;
    this.props.todoactions.toggle(todoToToggle);
	}

	destroy (todo) {
    this.props.todoactions.deleteTodo(todo);
	}

	edit (todo) {
		this.setState({editing: todo.id});
	}

	save (todoToSave, text) {
    todoToSave.title = text;
    this.props.todoactions.updateTodo(todoToSave);
		this.setState({editing: null});
	}

	cancel () {
		this.setState({editing: null});
	}

	clearCompleted () {
    const todosToClear = this.props.todostore.getTodos().filter(function (todo) {
			return todo.completed;
		});

		this.props.todoactions.deleteTodos(todosToClear);
	}

  render(){
    let footer, main;
    let todos = this.props.todostore.getTodos();

    let shownTodos = todos.filter(function (todo) {
				switch (this.state.nowShowing) {
				case TodoApp.ACTIVE_TODOS:
					return !todo.completed;
				case TodoApp.COMPLETED_TODOS:
					return todo.completed;
				default:
					return true;
				}
			}, this);

		var todoItems = shownTodos.map(function (todo) {
			return (
				<TodoItem
					key={todo.id}
					todo={todo}
					onToggle={this.toggle.bind(this, todo)}
					onDestroy={this.destroy.bind(this, todo)}
					onEdit={this.edit.bind(this, todo)}
					editing={this.state.editing === todo.id}
					onSave={this.save.bind(this, todo)}
					onCancel={this.cancel.bind(this)}
				/>
			);
		}, this);

		var activeTodoCount = todos.reduce(function (accum, todo) {
			return todo.completed ? accum : accum + 1;
		}, 0);

    var completedCount = todos.length - activeTodoCount;

		if (activeTodoCount || completedCount) {
			footer =
				<TodoFooter
					count={activeTodoCount}
					completedCount={completedCount}
					nowShowing={this.state.nowShowing}
					onClearCompleted={this.clearCompleted.bind(this)}
				/>;
		}

		if (todos.length) {
			main = (
				<section className="main">
					<input
						className="toggle-all"
						type="checkbox"
						onChange={this.toggleAll.bind(this)}
						checked={activeTodoCount === 0}
					/>
					<ul className="todo-list">
						{todoItems}
					</ul>
				</section>
			);
		}

    return (
      <div>
        <header className="header">
          <h1>todos</h1>
          <input
            className="new-todo"
            placeholder="What needs to be done?"
            value={this.state.newTodo}
            onKeyDown={this.handleNewTodoKeyDown.bind(this)}
            onChange={this.handleChange.bind(this)}
            autoFocus={true}
          />
        </header>
        {main}
        {footer}
      </div>
    );
  }
}
