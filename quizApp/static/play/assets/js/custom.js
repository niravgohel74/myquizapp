$(".option input").on("click", function () {
  $(".option").removeClass("selected");
  $(this).parent().addClass("selected");
});

var svgCircle = $(".counter circle");
var count = parseInt($(".counterContainer span").text());
var maxOffset = 471;
var interval = setInterval(function () {
  if (count <= 0) {
    clearInterval(interval);
  } else {
    var offset = maxOffset - Math.floor((count / initialCount) * maxOffset);
    svgCircle.css("stroke-dashoffset", offset);
    count--;
  }
  document.getElementById("countdown-timer").innerHTML = count;
}, 1000);

// Store the initial count to calculate the offset
var initialCount = count;

// next prev
var divs = $(".show-section fieldset");
var now = 0; // currently shown div
divs.hide().first().show(); // hide all divs except first

function next() {
  divs.eq(now).hide();
  now = now + 1 < divs.length ? now + 1 : 0;
  divs.eq(now).show(); // show next
  console.log(now);
  $(".question .fill").css("width", now * 25 + "%");
}
$(".prev").on("click", function () {
  divs.eq(now).hide();
  now = now > 0 ? now - 1 : divs.length - 1;
  divs.eq(now).show(); // show previous
  console.log(now);
  $(".question .fill").css("width", now * 25 + "%");

  $(".option").addClass("animate");
  $(".option").removeClass("animateReverse");
  $(".question h1").addClass("animate");
  $(".question h1").removeClass("animateReverse");
});

// quiz validation
var checkedradio = false;

function radiovalidate(stepnumber) {
  var checkradio = $("#step" + stepnumber + " input")
    .map(function () {
      if ($(this).is(":checked")) {
        return true;
      } else {
        return false;
      }
    })
    .get();

  checkedradio = checkradio.some(Boolean);
}

$(document).ready(function () {
  $(".question .fill").css("width", "0");
  // check step1
  $("#step1btn").on("click", function () {
    radiovalidate(1);

    if (checkedradio == false) {
      (function (el) {
        setTimeout(function () {
          el.children().remove(".reveal");
        }, 3000);
      })(
        $("#error").append(
          '<div class="reveal alert alert-danger">Choose an option!</div>'
        )
      );

      radiovalidate(1);
    } else {
      $("#step1 .option").removeClass("animate");
      $("#step1 .option").addClass("animateReverse");
      $("#step1 .question h1").removeClass("animate");
      $("#step1 .question h1").addClass("animateReverse");
      setTimeout(function () {
        next();
      }, 900);
      countresult(1);
    }
  });
  // check step2
  $("#step2btn").on("click", function () {
    radiovalidate(2);

    if (checkedradio == false) {
      (function (el) {
        setTimeout(function () {
          el.children().remove(".reveal");
        }, 3000);
      })(
        $("#error").append(
          '<div class="reveal alert alert-danger">Choose an option!</div>'
        )
      );

      radiovalidate(2);
    } else {
      $("#step2 .option").removeClass("animate");
      $("#step2 .option").addClass("animateReverse");
      $("#step2 .question h1").removeClass("animate");
      $("#step2 .question h1").addClass("animateReverse");
      setTimeout(function () {
        next();
      }, 900);
      countresult(2);
    }
  });
  // check step3
  $("#step3btn").on("click", function () {
    radiovalidate(3);

    if (checkedradio == false) {
      (function (el) {
        setTimeout(function () {
          el.children().remove(".reveal");
        }, 3000);
      })(
        $("#error").append(
          '<div class="reveal alert alert-danger">Choose an option!</div>'
        )
      );

      radiovalidate(3);
    } else {
      $("#step3 .option").removeClass("animate");
      $("#step3 .option").addClass("animateReverse");
      $("#step3 .question h1").removeClass("animate");
      $("#step3 .question h1").addClass("animateReverse");
      setTimeout(function () {
        next();
      }, 900);
      countresult(3);
    }
  });
  // check step4
  $("#sub").on("click", function () {
    radiovalidate(4);

    if (checkedradio == false) {
      (function (el) {
        setTimeout(function () {
          el.children().remove(".reveal");
        }, 3000);
      })(
        $("#error").append(
          '<div class="reveal alert alert-danger">Choose an option!</div>'
        )
      );

      radiovalidate(4);
    } else {
      countresult(4);
      showresult();
    }
  });
});
