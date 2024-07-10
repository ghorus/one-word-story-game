var socket = io();

socket.on("connect", () => {
    console.log(socket.connected); // true
    socket.emit('connect')
  });

function test(){
  var message = document.querySelector(".massage").value
  var room = document.querySelector(".rm").value
  socket.emit("test",{"message":message,"room":room})
}

socket.on("test",(data)=>{
  var p = document.querySelector(".title")
  var pp = document.querySelector(".dash")
  p.innerText = data
  pp.innerText = data
})

socket.on('updateConnected',(members_data)=>{
  var members = document.querySelectorAll(".member")
  for(i=0;i<members.length;i++){
    members[i].remove()
  }
  var members_container = document.querySelector(".small-box")
  for(i=0;i<members_data.length;i++){
    var div = document.createElement("div")
    var span = document.createElement("span")
    div.classList.add("member")
    div.setAttribute("id", members_data[i]["member_id"]) 
    div.setAttribute("onmouseover", "highlight()") 
    if(members_data[i]["host"] == true){
      span.innerText = members_data[i]["username"] + " (Host) "
    }
    else{
      span.innerText = members_data[i]["username"]
    }
    div.appendChild(span)
    members_container.appendChild(div)
  }
})
var c = 0
function highlight(){
  var members = document.getElementsByClassName("member")
  var messages = document.getElementsByClassName("message")

    for (i=0;i <members.length;i++){
    
        for(j=0;j<messages.length;j++){
            if(event.target.id==messages[j].id){
                messages[j].style.backgroundColor = "#5ba48e"
                messages[j].style.borderRadius = "5px"
                messages[j].style.padding = "0px 1px"
            }
        }
  
        members[i].addEventListener("mouseleave",()=>{
            for(j=0;j<messages.length;j++){
                messages[j].style.backgroundColor = "transparent"
                messages[j].style.padding = "initial"
            }
        })
    }
}

function joinRoom (room_code){
  socket.emit("joinRoom",room_code)
}

function createRoom(){
  socket.emit("createRoom")
}

socket.on('redirect',(dest)=>{
  window.location.href = dest;
})
// function createRoom (){
//   socket.emit("createRoom")
// }
function leaveRoom (){
  socket.emit("leave")
}

function sendMessage (room_id,room_code,user_id){
  var input = document.querySelector(".message-input")
  var input_value = input.value
  input.value = ""

  var data = {
    "input_value": input_value,
    "room_id": room_id,
    "room_code":room_code,
    "user_id":user_id
  }
  socket.emit("sendMessage",data)
}

function enterMessage(room_id,room_code,user_id){
  if(event.key === 'Enter') {
    sendMessage(room_id,room_code,user_id)
}
}

let timeout 
socket.on("warn",(message)=>{
  var socketBroadcast = document.querySelector(".socket-broadcast")
  socketBroadcast.children[0].innerText = message
  socketBroadcast.children[0].classList.add("info")
  clearTimeout(timeout)
  timeout = setTimeout(()=>{
    socketBroadcast.children[0].innerText = ""
    socketBroadcast.children[0].classList.remove("info")
  }, 3000)
})
socket.on("sendMessage", (data) => {
  //update messages
  var messages_container = document.querySelector(".messages")
  var new_message = document.createElement("SPAN")
  new_message.id = data["user_id"]
  new_message.innerText = data["message"]
  new_message.classList.add("message")
  messages_container.appendChild(new_message)
  var text = document.createTextNode(' ');
  messages_container.appendChild(text)

  //update turn
  var member_turn = document.querySelector(".member-turn")
  member_turn.innerText = data["next_turn"] + "'s turn!"
})