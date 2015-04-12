$(function() {
  "use strict";

  // Set email link with JS (to mess with spambots just a little)
  $("#email-link").attr("href", [
    "m","a","i","l","t","o",":",
    "n","t","r","r","g","c",
    "@","g","m","a","i","l",
    ".","c","o","m"
  ].join(""));

  // Move odd images to the left on wide screen, leaving them below in narrow
  // screens.
  if (!window.matchMedia) {
    // Unsupported in this browser.
    return;
  }
  var alternated = false;

  var ensureAlternated = function() {
    if (!alternated) {
      $(".showcase:odd").each(function(i, showcase) {
        console.log(showcase);
        $(showcase).addClass("even");
        $(".showcase-picture", showcase)
          .detach()
          .prependTo(showcase);
      });
      alternated = true;
    }
  };
  var ensureNotAlternated = function() {
    if (alternated) {
      $(".showcase:odd").each(function(i, showcase) {
        $(showcase).removeClass("even");
        $(".showcase-picture", showcase)
          .detach()
          .appendTo(showcase);
      });
      alternated = false;
    }
  };

  var updateAlternate = function() {
    if (window.matchMedia("(min-width: 992px)").matches) {
      ensureAlternated();
    } else {
      ensureNotAlternated();
    }
  };

  $(window).resize(updateAlternate)
  updateAlternate();
});
