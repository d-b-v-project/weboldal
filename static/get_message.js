
function get_message() {
    fetch("/api/1103")
    .then(response => response.json())
    .then(data => {
      var messages = document.getElementById("messages")
      messages.innerText=""
      for(var i of data){
        messages.innerHTML += `<div class="msg">${i[0]}: ${i[1]} | ${i[2]} <br class="padding"></div>`
      }
      
  
    })
    .catch(error => console.log(error))
    
}
const intervalId = setInterval(get_message, 1500);


const scrollableDiv = document.getElementById('chat-box');
const chatContainer = document.getElementById('chat-box');

// Function to scroll to bottom

document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('chat-box');
    let shouldAutoScroll = true;
    function scrollToBottom() {
        if (!container) {
          console.error('Container not found!');
          return;
        }
    
        // Try multiple methods to ensure cross-browser compatibility
        container.scrollTop = container.scrollHeight;
        container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
        
        // Alternative method if needed
        const lastChild = container.lastElementChild;
        if (lastChild) {
          lastChild.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }
    }
    container.addEventListener('scroll', function() {
        const threshold = 50; // pixels from bottom
        shouldAutoScroll = (container.scrollTop + container.clientHeight + threshold) >= container.scrollHeight;
      });
    
      // 5. Test with periodic messages
      setInterval(function() {
        scrollToBottom()
      }, 2000);
    
      // 6. Initial scroll
      setTimeout(scrollToBottom, 100); // Small delay to ensure rendering
});