_.ensure = function(collection, condition, newElement) {
  var index = this.findIndex(collection, condition);
  if (index != -1) {
    return collection[index];
  } else {
    collection.push(newElement);
    return newElement;
  }
}
