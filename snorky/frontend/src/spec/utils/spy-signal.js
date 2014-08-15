function spySignal(event) {
  var spy = jasmine.createSpy();
  event.add(spy);
  return spy;
}
