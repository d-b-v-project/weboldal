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

function get_message() {
  fetch("/api/1103")
  .then(response => response.json())
  .then(data => {
    for(var i of data){
      console.log(`${i[0]}: ${i[1]} | ${i[2]} <br>`)
      var messages = document.getElementById("messages").innerHTML = `${i[0]}: ${i[1]} | ${i[2]} <br><br>`
    }
  })
  .catch(error => console.log(error))
  
}
const intervalId = setInterval(get_message, 2000);


