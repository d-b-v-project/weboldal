function myFunction() {
  var x = document.getElementById("myTopnav");
  var y = document.getElementById("login");
  if (x.className === "topnav") {
    y.style.display = "none"
    x.className += " responsive";
  } else {
    y.style.display = "block"
    x.className = "topnav";
  }
}

function myFunctions() {
var x = document.getElementById("myTopnav");
if (x.className === "topnav") {
  x.className += " responsive";
} else {
  x.className = "topnav";
}
}

