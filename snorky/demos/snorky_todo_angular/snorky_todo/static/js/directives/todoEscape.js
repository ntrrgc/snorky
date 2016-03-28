// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

/*global angular */

/**
 * Directive that executes an expression when the element it is applied to gets
 * an `escape` keydown event.
 */
angular.module('todomvc')
	.directive('todoEscape', function () {
		'use strict';

		var ESCAPE_KEY = 27;

		return function (scope, elem, attrs) {
			elem.bind('keydown', function (event) {
				if (event.keyCode === ESCAPE_KEY) {
					scope.$apply(attrs.todoEscape);
				}
			});
		};
	});
