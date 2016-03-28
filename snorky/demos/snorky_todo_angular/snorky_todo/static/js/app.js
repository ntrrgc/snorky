// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

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
