import React from 'react';
import ReactDOM from 'react-dom';
import TodoApp from './components/TodoApp';
import TodoModel from './models/TodoModel';
import TodoActions from './actions/TodoActions';
import TodoStore from './stores/TodoStore';

let model = new TodoModel('react-todos');
const todoactions = new TodoActions({ apiendpoint: "/api" });
const todostore = new TodoStore({ actions: todoactions });
// Render the main component into the dom
function render(){
  ReactDOM.render(<TodoApp todoactions={todoactions}
                           todostore={todostore}
                           model={model} />,
                  document.getElementById('todoapp'));
}
model.subscribe(render);
render();
