/*global angular */

/**
 * The main TodoMVC app module
 *
 * @type {angular.Module}
 */
angular.module('todomvc', ['ngRoute', 'restangular', 'Snorky'])
	.config(function ($routeProvider, $locationProvider) {
		'use strict';

    $locationProvider.html5Mode(true);

		$routeProvider.when('/', {
			controller: 'TodoCtrl',
			templateUrl: 'todomvc-index.html'
		}).when('/:status', {
			controller: 'TodoCtrl',
			templateUrl: 'todomvc-index.html'
		}).otherwise({
			redirectTo: '/'
		});
	});
