from flask import render_template, redirect,flash,url_for,Blueprint
from flask_login import current_user,login_required
from one_word.models import ChatRoom,User,Message,StoryPost
from one_word import db,socket,app
from flask_socketio import emit,join_room,leave_room
import random
import string

game = Blueprint('game',__name__)

@game.route("/test")
def test():
    return render_template("test.html")
@socket.on("test")
def tester(data):
    c = ChatRoom.query.filter_by(id=current_user.chatroom_id).first()
    app.logger.warning(c.code==data['room'])
    join_room(data["room"])
    emit("warn",data['message'],room=data['room'])
    emit("test",data["message"],room=data["room"])

@game.route('/room_lobby')
def room_lobby():
    rooms = ChatRoom.query.all()
    return render_template('room_lobby.html',rooms=rooms)


@game.route('/game_room/<room_id>')
@login_required
def game_room(room_id):
    room = ChatRoom.query.filter_by(id=room_id).first()
    return render_template('game_room.html',room=room)

# @game.route('/create_room')
# @login_required
# def create_room():
#     if current_user.chatroom_id != None:
#         existing_room = current_user.chatroom_id
#         room = ChatRoom.query.filter_by(id=existing_room).first()
#         flash(f'You are already in a room ( {room.code} ). Please leave it to create another one.','danger')
#         return redirect(url_for('game.room_lobby'))
#     else:
#         new_room_code = generate_unique_code()
#         new_room = ChatRoom(host=current_user.id,code=new_room_code)
#         db.session.add(new_room)
#         db.session.commit()
#         current_user.chatroom_id = new_room.id
#         db.session.commit()
#     return redirect(url_for('game.game_room',room_id=new_room.id))

@socket.on('createRoom')
def create_room():
    if current_user.chatroom_id != None:
        existing_room = current_user.chatroom_id
        room = ChatRoom.query.filter_by(id=existing_room).first()
        emit('warn',f'You are already in a room ( {room.code} ). Please leave it to create another one.')
    else:
        new_room_code = generate_unique_code()
        new_room = ChatRoom(host=current_user.id,code=new_room_code,turn=current_user.id)
        db.session.add(new_room)
        db.session.commit()
        current_user.chatroom_id = new_room.id
        db.session.commit()
        emit('redirect',url_for('game.game_room',room_id=new_room.id))
    
@socket.on('joinRoom')
def joinRoom(chatroom_code):
    chatroom = ChatRoom.query.filter_by(code=chatroom_code).first()
    existing_room = ChatRoom.query.filter_by(id=current_user.chatroom_id).first()
    if chatroom:
        room =chatroom.code
        if existing_room:
            if existing_room.code != chatroom.code:
                emit('warn',f'You are already in another room ( #{existing_room.code} ). Please leave it to join room #{chatroom_code}.')
            elif existing_room.code == chatroom.code:
                members_data = []
                for member in chatroom.members:
                    is_host= True if member.id == chatroom.host else False
                    members_data.append({
                        "member_id":member.id,
                        "username":member.username,
                        "host":is_host})

                emit('updateConnected',members_data,room=room)
                emit('redirect',url_for('game.game_room',room_id=chatroom.id))
        elif not existing_room:
            current_user.chatroom_id = chatroom.id
            db.session.commit()

            members_data = []
            for member in chatroom.members:
                is_host= True if member.id == chatroom.host else False
                members_data.append({
                    "member_id":member.id,
                    "username":member.username,
                    "host":is_host})

            emit('updateConnected',members_data,room=room)
            emit('redirect',url_for('game.game_room',room_id=chatroom.id))

    elif not chatroom:
        emit('warn',f'Room does not exist anymore.')
        emit('redirect',url_for('game.room_lobby'))

# # @game.route('/delete_room/<room_id>')
# # def delete_room(room_id):
# #     if ChatRoom.query.filter_by(id=room_id).first():
# #         ChatRoom.query.filter_by(id=room_id).delete()
# #         chatroom_member = User.query.filter_by(chatroom_id=room_id).first()
# #         if chatroom_member:
# #             chatroom_member.chatroom_id = None
# #         db.session.commit()
# #         flash("Room deleted.",'success')
# #         return redirect(url_for('game.room_lobby'))

def generate_unique_code():
    times_checked = 0
    while True:
        # Generate a 4-character code
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        chatroom_code = ChatRoom.query.filter_by(code=code).first()
        if not chatroom_code:
            return code
        times_checked += 1
        if times_checked == 10:
            raise TimeoutError('Could not generate room code')
        
@socket.on("sendMessage")
def send_message(data):
    chatroom = ChatRoom.query.filter_by(code=data["room_code"]).first()
    app.logger.warning(chatroom.members)
    room = data["room_code"]
    user_id = int(data["user_id"])
    if user_id == chatroom.turn:
        if len((data["input_value"]).split()) > 1:
            emit('warn',"One word only, please.")
        else:
            #submit message and update turn
            msg = Message(message=data["input_value"],user_id=current_user.id,chatroom_id=current_user.chatroom_id)
            next_turn = 0
            members = chatroom.members
            for i in range(len(members)):
                if members[i].id == chatroom.turn:
                    next_turn = i + 1 if i + 1 < len(members) else 0
            chatroom.turn = members[next_turn].id
            db.session.add(msg)
            db.session.commit()
            username = members[next_turn].username
            message_data = {"message":msg.message,"user_id":msg.user_id,"next_turn":username}

            # emit("warn",'hi :D',room=room)
            emit("sendMessage",message_data,room=room)
    elif user_id != chatroom.turn:
        emit("warn","It's not your turn!")

@socket.on('connect')
def connect():
    if current_user.is_authenticated:
        chatroom = ChatRoom.query.filter_by(id=current_user.chatroom_id).first()
        if chatroom:
            room = chatroom.code
            join_room(room)

@socket.on("leave")
def leave():
    user = User.query.filter_by(id=current_user.id).first()
    chatroom = ChatRoom.query.filter_by(id=user.chatroom_id).first()
    leave_room(chatroom.code)
    if current_user.chatroom_id:
        current_user.chatroom_id = None
        db.session.commit()

    if chatroom.members:
        members = chatroom.members
        if current_user.id == chatroom.host:
            chatroom.host = [member.id for member in members][0]

            next_turn = 0
            for i in range(len(members)):
                if members[i].id == current_user.id:
                    next_turn = i + 1 if i < len(members) else 0
            chatroom.turn = members[next_turn].id
            db.session.commit()
        members_data = []
        for member in chatroom.members:
            is_host= True if member.id == chatroom.host else False
            members_data.append({
                "member_id":member.id,
                "username":member.username,
                "host":is_host})

        emit('updateConnected',members_data,room=chatroom.code)
        emit("warn",f'{user.username} has left.',room=chatroom.code,include_self=False)
        emit("redirect",url_for('game.room_lobby'))

    if not chatroom.members:
       ChatRoom.query.filter_by(id=chatroom.id).delete()
       Message.query.filter_by(chatroom_id=chatroom.id).delete()
       db.session.commit()
       emit("redirect",url_for('game.room_lobby'))

@game.route("/submit_story/<room_id>")
def submit_story(room_id):
    room = ChatRoom.query.filter_by(id=int(room_id)).first()
    members = [member.username for member in room.members]
    msg = [message.message for message in room.messages]
    app.logger.warning(msg)
    if msg:
        story = " ".join(msg)
        authors = " ".join(members)
        new_story = StoryPost(story=story,authors=authors)
        db.session.add(new_story)
        db.session.delete(room)
        db.session.commit()
        return redirect(url_for('main.read_stories'))
    