// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

_.ensure = function(collection, condition, newElement) {
  var index = this.findIndex(collection, condition);
  if (index != -1) {
    return collection[index];
  } else {
    collection.push(newElement);
    return newElement;
  }
}
