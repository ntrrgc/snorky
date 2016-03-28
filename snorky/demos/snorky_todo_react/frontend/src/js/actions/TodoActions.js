'use strict';

import { Action } from 'geiger';
import axios from 'axios';

//import { TodoRecord } from '../records';
import {uuid} from '../utils/Utils';
import TodoItem from '../components/TodoItem';

export default class TodoActions extends Action {

    constructor({ apiendpoint }) {
        super();
        this.apiendpoint = apiendpoint;
        this.todos = [];
    }

    getAllTodos () {
      return this.todos;
    }

    fetchTodos() {
        return axios
            .get(this.apiendpoint + '/tasks')
            //.then(todos => todos.data.slice(0, 7).map(o => <TodoItem />)  // passed to the store after REST response (obviously); sliced for the demo
            .then(todos => {this.todos = todos; this.emit('fetchTodos', todos)});
    }

    fetchTodosAndSubscribe(){
      return axios
        .get(this.apiendpoint + '/tasks', {headers:{"X-Snorky":"Subscribe"}})
        .then(todos => {
          this.subscriptionToken = todos.headers["x-subscription-token"];

          this.todos = todos.data;
          this.snorky = new Snorky(WebSocket, "ws://localhost:5001/ws",{
            "datasync": Snorky.DataSync
          });
          var deltaProcessor = new Snorky.DataSync.CollectionDeltaProcessor({

          });
          this.deltaProcesor = deltaProcessor;
          this.snorky.services.datasync.onDelta = function(delta){
            // Called each time a data change notification (delta) is received.
            // CollectionDeltaProcessor is a class that applies these deltas
            // in a collection (usually an array).
            deltaProcessor.processDelta(delta);
            this.emit("snorky", this.todos);

            // Here we could also inspect the delta element and show alerts to the
            // user or play a sound when data changes.
          }.bind(this);
          var todoCollection = new Snorky.DataSync.ArrayCollection(this.todos, {
            //transformItem: function(item) {
              // Allows us to define how a data element received from a delta as
              // simple JSON will be translated to an element of this array.

              // This is useful if we use fat elements (e.g. each element has a
              // .delete() method).
              /*return Restangular.restangularizeElement(
                null, item, "tasks", true, response.data, null
              );
            }*/
          });

          deltaProcessor.collections["Task"] = todoCollection;
          this.snorky.services.datasync.acquireSubscription({
            token: this.subscriptionToken
          });
          this.emit('fetchTodos', this.todos)
        });
    }

    createTodo(title) {
        const todo = {title, complete:false};
        return axios.post(this.apiendpoint + '/tasks', todo);   // passed to the store without awaiting REST response for optimistic add
    }

    toggle(todoToToggle){
        axios.put(this.apiendpoint+"/tasks/"+todoToToggle.id, todoToToggle);
    }

    toggleAll(checked){
      for(let todo of this.todos){
        todo.completed = checked;
        axios.put(this.apiendpoint + "/tasks/"+todo.id, todo);
      }
    }

    deleteTodo(todo) {
        return axios.delete(this.apiendpoint + '/tasks/' + todo.id);
    }

    deleteTodos(todos){
      if(todos.length > 0){
        var index = 0;
          var deleteNext = function(index){
            if(index < todos.length){
              axios.delete(this.apiendpoint + '/tasks/'+todos[index].id)
                .then(deleteNext.bind(this, index+1))
            }
          }
          axios.delete(this.apiendpoint + '/tasks/'+todos[index].id)
            .then(deleteNext.bind(this, index+1))
      }
    }

    updateTodo(todo){
      return axios.put(this.apiendpoint+'/tasks/'+todo.id, todo);
    }
}
