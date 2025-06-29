import os
from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from sqlalchemy import or_, desc
from urllib.parse import urlparse
from app import app, db
from models import (User, Note, Post, Comment, Like, Achievement, Mission, UserAchievement, UserMission, 
                   Message, MarketplaceItem, ChatConversation, ChatMessage, Notification, DailyStreak,
                   Referral, Course, CourseVideo, CourseEnrollment, WeeklyRanking, MonthlyRanking)
from forms import RegistrationForm, LoginForm, NoteUploadForm, PostForm, CommentForm, MessageForm, ProfileEditForm, MarketplaceItemForm
from utils import (upload_file_to_cloudinary, get_file_type, award_crolars, check_achievements, 
                  create_default_achievements, create_default_missions, format_time_ago,
                  generate_referral_code, create_notification, update_daily_streak, process_ai_response)
from datetime import datetime

# Initialize default data
with app.app_context():
    create_default_achievements()
    create_default_missions()

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('feed'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('feed'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            career=form.career.data,
            university=form.university.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        # Award welcome Crolars
        award_crolars(user, 'complete_profile')
        
        flash('¡Registro exitoso! Bienvenido a CRUNEVO.', 'success')
        login_user(user)
        return redirect(url_for('feed'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('feed'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Try to find user by username or email
        user = User.query.filter(
            or_(User.username == form.username.data, User.email == form.username.data)
        ).first()
        
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('feed')
            
            # Award daily login Crolars
            award_crolars(user, 'daily_login')
            
            flash(f'¡Bienvenido de vuelta, {user.first_name}!', 'success')
            return redirect(next_page)
        else:
            flash('Nombre de usuario/email o contraseña incorrectos.', 'error')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('index'))

@app.route('/feed')
@login_required
def feed():
    page = request.args.get('page', 1, type=int)
    
    # Get recent notes and posts
    notes = Note.query.filter_by(is_public=True).order_by(desc(Note.created_at)).limit(10).all()
    posts = Post.query.order_by(desc(Post.created_at)).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # Get user's active missions
    active_missions = Mission.query.filter_by(is_active=True).limit(3).all()
    
    # Get top contributors this week
    top_users = User.query.order_by(desc(User.total_points)).limit(5).all()
    
    post_form = PostForm()
    
    return render_template('feed.html', 
                         posts=posts, 
                         notes=notes, 
                         post_form=post_form,
                         active_missions=active_missions,
                         top_users=top_users,
                         format_time_ago=format_time_ago)

@app.route('/create_post', methods=['POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            content=form.content.data,
            post_type=form.post_type.data,
            subject=form.subject.data,
            user_id=current_user.id
        )
        db.session.add(post)
        db.session.commit()
        
        # Award Crolars for posting
        award_crolars(current_user, 'comment')
        
        flash('¡Publicación creada exitosamente!', 'success')
    
    return redirect(url_for('feed'))

@app.route('/upload_note', methods=['GET', 'POST'])
@login_required
def upload_note():
    form = NoteUploadForm()
    if form.validate_on_submit():
        # Upload file to Cloudinary
        file_data = upload_file_to_cloudinary(form.file.data, "notes")
        
        if file_data:
            note = Note(
                title=form.title.data,
                description=form.description.data,
                subject=form.subject.data,
                career=form.career.data,
                file_url=file_data['url'],
                file_type=get_file_type(form.file.data.filename),
                thumbnail_url=file_data['url'] if file_data['resource_type'] == 'image' else None,
                is_public=form.is_public.data,
                user_id=current_user.id
            )
            
            db.session.add(note)
            db.session.commit()
            
            # Award Crolars and check achievements
            award_crolars(current_user, 'upload_note')
            if len(current_user.notes) == 1:
                award_crolars(current_user, 'first_note')
            check_achievements(current_user)
            
            flash('¡Nota subida exitosamente! Has ganado Crolars.', 'success')
            return redirect(url_for('note_detail', id=note.id))
        else:
            flash('Error al subir el archivo. Inténtalo de nuevo.', 'error')
    
    return render_template('upload_note.html', form=form)

@app.route('/note/<int:id>')
def note_detail(id):
    note = Note.query.get_or_404(id)
    
    # Increment view count
    note.views += 1
    db.session.commit()
    
    # Get comments
    comments = Comment.query.filter_by(note_id=id).order_by(Comment.created_at).all()
    
    comment_form = CommentForm()
    
    return render_template('note_detail.html', 
                         note=note, 
                         comments=comments, 
                         comment_form=comment_form,
                         format_time_ago=format_time_ago)

@app.route('/add_comment/<string:content_type>/<int:content_id>', methods=['POST'])
@login_required
def add_comment(content_type, content_id):
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            user_id=current_user.id
        )
        
        if content_type == 'note':
            comment.note_id = content_id
            redirect_url = url_for('note_detail', id=content_id)
        elif content_type == 'post':
            comment.post_id = content_id
            redirect_url = url_for('feed')
        
        db.session.add(comment)
        db.session.commit()
        
        # Award Crolars for commenting
        award_crolars(current_user, 'comment')
        
        flash('Comentario agregado exitosamente.', 'success')
        return redirect(redirect_url)
    
    return redirect(url_for('feed'))

@app.route('/like/<string:content_type>/<int:content_id>')
@login_required
def toggle_like(content_type, content_id):
    # Check if user already liked this content
    existing_like = None
    content_obj = None
    
    if content_type == 'note':
        existing_like = Like.query.filter_by(user_id=current_user.id, note_id=content_id).first()
        content_obj = Note.query.get_or_404(content_id)
    elif content_type == 'post':
        existing_like = Like.query.filter_by(user_id=current_user.id, post_id=content_id).first()
        content_obj = Post.query.get_or_404(content_id)
    elif content_type == 'comment':
        existing_like = Like.query.filter_by(user_id=current_user.id, comment_id=content_id).first()
        content_obj = Comment.query.get_or_404(content_id)
    
    if existing_like:
        # Unlike
        db.session.delete(existing_like)
        content_obj.likes -= 1
    else:
        # Like
        like = Like(user_id=current_user.id)
        if content_type == 'note':
            like.note_id = content_id
        elif content_type == 'post':
            like.post_id = content_id
        elif content_type == 'comment':
            like.comment_id = content_id
        
        db.session.add(like)
        content_obj.likes += 1
        
        # Award Crolars to content author
        if content_obj.author != current_user:
            award_crolars(content_obj.author, 'receive_like')
    
    db.session.commit()
    
    return redirect(request.referrer or url_for('feed'))

@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    # Get user's notes and posts
    notes = Note.query.filter_by(user_id=user.id, is_public=True).order_by(desc(Note.created_at)).limit(10).all()
    posts = Post.query.filter_by(user_id=user.id).order_by(desc(Post.created_at)).limit(10).all()
    
    # Get user's achievements
    achievements = UserAchievement.query.filter_by(user_id=user.id).all()
    
    return render_template('profile.html', 
                         user=user, 
                         notes=notes, 
                         posts=posts, 
                         achievements=achievements,
                         format_time_ago=format_time_ago)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileEditForm()
    
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.bio = form.bio.data
        current_user.career = form.career.data
        current_user.university = form.university.data
        
        db.session.commit()
        flash('Perfil actualizado exitosamente.', 'success')
        return redirect(url_for('profile', username=current_user.username))
    
    # Pre-populate form
    form.first_name.data = current_user.first_name
    form.last_name.data = current_user.last_name
    form.bio.data = current_user.bio
    form.career.data = current_user.career
    form.university.data = current_user.university
    
    return render_template('edit_profile.html', form=form)

@app.route('/forum')
@login_required
def forum():
    page = request.args.get('page', 1, type=int)
    filter_type = request.args.get('filter', 'all')
    
    query = Post.query
    
    if filter_type == 'questions':
        query = query.filter_by(post_type='question')
    elif filter_type == 'discussions':
        query = query.filter_by(post_type='discussion')
    
    posts = query.order_by(desc(Post.created_at)).paginate(
        page=page, per_page=15, error_out=False
    )
    
    return render_template('forum.html', posts=posts, filter_type=filter_type, format_time_ago=format_time_ago)

@app.route('/missions')
@login_required
def missions():
    # Get all active missions
    active_missions = Mission.query.filter_by(is_active=True).all()
    
    # Get user's mission progress
    user_missions = {}
    for mission in active_missions:
        user_mission = UserMission.query.filter_by(
            user_id=current_user.id, 
            mission_id=mission.id
        ).first()
        
        if not user_mission:
            # Create new user mission
            user_mission = UserMission(
                user_id=current_user.id,
                mission_id=mission.id
            )
            db.session.add(user_mission)
        
        user_missions[mission.id] = user_mission
    
    db.session.commit()
    
    return render_template('missions.html', 
                         missions=active_missions, 
                         user_missions=user_missions)

@app.route('/marketplace')
@login_required
def marketplace():
    page = request.args.get('page', 1, type=int)
    
    items = MarketplaceItem.query.filter_by(is_active=True).order_by(desc(MarketplaceItem.created_at)).paginate(
        page=page, per_page=12, error_out=False
    )
    
    return render_template('marketplace.html', items=items, format_time_ago=format_time_ago)

@app.route('/sell_item', methods=['GET', 'POST'])
@login_required
def sell_item():
    form = MarketplaceItemForm()
    
    if form.validate_on_submit():
        item = MarketplaceItem(
            title=form.title.data,
            description=form.description.data,
            price_crolars=form.price_crolars.data,
            item_type=form.item_type.data,
            stock=form.stock.data,
            seller_id=current_user.id
        )
        
        db.session.add(item)
        db.session.commit()
        
        flash('¡Artículo publicado en el marketplace!', 'success')
        return redirect(url_for('marketplace'))
    
    return render_template('sell_item.html', form=form)

@app.route('/messages')
@login_required
def messages():
    # Get conversations (unique senders/receivers)
    sent_messages = db.session.query(Message.receiver_id, User.username, User.first_name, User.last_name)\
        .join(User, Message.receiver_id == User.id)\
        .filter(Message.sender_id == current_user.id)\
        .distinct().all()
    
    received_messages = db.session.query(Message.sender_id, User.username, User.first_name, User.last_name)\
        .join(User, Message.sender_id == User.id)\
        .filter(Message.receiver_id == current_user.id)\
        .distinct().all()
    
    # Combine and deduplicate conversations
    conversations = {}
    for user_id, username, first_name, last_name in sent_messages + received_messages:
        if user_id != current_user.id:
            conversations[user_id] = {
                'username': username,
                'full_name': f"{first_name} {last_name}"
            }
    
    return render_template('messages.html', conversations=conversations)

@app.route('/chat/<username>')
@login_required
def chat(username):
    other_user = User.query.filter_by(username=username).first_or_404()
    
    # Get message history
    messages = Message.query.filter(
        or_(
            (Message.sender_id == current_user.id) & (Message.receiver_id == other_user.id),
            (Message.sender_id == other_user.id) & (Message.receiver_id == current_user.id)
        )
    ).order_by(Message.created_at).all()
    
    # Mark messages as read
    Message.query.filter_by(sender_id=other_user.id, receiver_id=current_user.id, read=False).update({'read': True})
    db.session.commit()
    
    form = MessageForm()
    
    return render_template('chat.html', 
                         other_user=other_user, 
                         messages=messages, 
                         form=form,
                         format_time_ago=format_time_ago)

@app.route('/send_message/<username>', methods=['POST'])
@login_required
def send_message(username):
    other_user = User.query.filter_by(username=username).first_or_404()
    form = MessageForm()
    
    if form.validate_on_submit():
        message = Message(
            content=form.content.data,
            sender_id=current_user.id,
            receiver_id=other_user.id
        )
        
        db.session.add(message)
        db.session.commit()
        
        flash('Mensaje enviado.', 'success')
    
    return redirect(url_for('chat', username=username))

@app.route('/search')
@login_required
def search():
    query = request.args.get('q', '')
    content_type = request.args.get('type', 'all')
    
    results = {
        'notes': [],
        'posts': [],
        'users': []
    }
    
    if query:
        if content_type in ['all', 'notes']:
            results['notes'] = Note.query.filter(
                Note.title.contains(query) | Note.description.contains(query),
                Note.is_public == True
            ).limit(10).all()
        
        if content_type in ['all', 'posts']:
            results['posts'] = Post.query.filter(
                Post.content.contains(query)
            ).limit(10).all()
        
        if content_type in ['all', 'users']:
            results['users'] = User.query.filter(
                User.username.contains(query) | 
                User.first_name.contains(query) | 
                User.last_name.contains(query)
            ).limit(10).all()
    
    return render_template('search_results.html', 
                         query=query, 
                         results=results, 
                         content_type=content_type,
                         format_time_ago=format_time_ago)

# Context processors
@app.context_processor
def utility_processor():
    return dict(format_time_ago=format_time_ago)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# AI Chatbot Routes
@app.route('/crunebot')
@login_required
def crunebot():
    """AI chatbot page"""
    conversations = ChatConversation.query.filter_by(user_id=current_user.id).order_by(ChatConversation.updated_at.desc()).all()
    return render_template('crunebot.html', conversations=conversations)

@app.route('/crunebot/new', methods=['POST'])
@login_required
def new_conversation():
    """Create new AI conversation"""
    data = request.get_json()
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'error': 'Mensaje requerido'}), 400
    
    # Create new conversation
    conversation = ChatConversation(
        user_id=current_user.id,
        title=message[:50] + ('...' if len(message) > 50 else '')
    )
    db.session.add(conversation)
    db.session.flush()
    
    # Add user message
    user_message = ChatMessage(
        conversation_id=conversation.id,
        content=message,
        is_user_message=True
    )
    db.session.add(user_message)
    
    # Process AI response
    ai_response = process_ai_response(message, conversation.id)
    ai_message = ChatMessage(
        conversation_id=conversation.id,
        content=ai_response,
        is_user_message=False
    )
    db.session.add(ai_message)
    db.session.commit()
    
    return jsonify({
        'conversation_id': conversation.id,
        'title': conversation.title,
        'user_message': message,
        'ai_response': ai_response
    })

@app.route('/crunebot/conversation/<int:conversation_id>')
@login_required
def get_conversation(conversation_id):
    """Get conversation messages"""
    conversation = ChatConversation.query.filter_by(
        id=conversation_id, 
        user_id=current_user.id
    ).first_or_404()
    
    messages = ChatMessage.query.filter_by(
        conversation_id=conversation_id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    return jsonify({
        'conversation': {
            'id': conversation.id,
            'title': conversation.title,
            'created_at': conversation.created_at.isoformat()
        },
        'messages': [{
            'id': msg.id,
            'content': msg.content,
            'is_user_message': msg.is_user_message,
            'created_at': msg.created_at.isoformat()
        } for msg in messages]
    })

@app.route('/crunebot/conversation/<int:conversation_id>/message', methods=['POST'])
@login_required
def add_message_to_conversation(conversation_id):
    """Add message to existing conversation"""
    conversation = ChatConversation.query.filter_by(
        id=conversation_id, 
        user_id=current_user.id
    ).first_or_404()
    
    data = request.get_json()
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'error': 'Mensaje requerido'}), 400
    
    # Add user message
    user_message = ChatMessage(
        conversation_id=conversation_id,
        content=message,
        is_user_message=True
    )
    db.session.add(user_message)
    
    # Process AI response
    ai_response = process_ai_response(message, conversation_id)
    ai_message = ChatMessage(
        conversation_id=conversation_id,
        content=ai_response,
        is_user_message=False
    )
    db.session.add(ai_message)
    
    conversation.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'user_message': message,
        'ai_response': ai_response
    })

# Notifications Routes
@app.route('/notifications')
@login_required
def notifications():
    """User notifications page"""
    page = request.args.get('page', 1, type=int)
    notifications = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    
    # Mark notifications as read when viewed
    unread_notifications = Notification.query.filter_by(
        user_id=current_user.id, 
        is_read=False
    ).all()
    for notification in unread_notifications:
        notification.is_read = True
    db.session.commit()
    
    return render_template('notifications.html', notifications=notifications)

@app.route('/notifications/unread-count')
@login_required
def unread_notifications_count():
    """Get count of unread notifications"""
    count = Notification.query.filter_by(
        user_id=current_user.id, 
        is_read=False
    ).count()
    return jsonify({'count': count})

# Rankings and Leaderboards
@app.route('/rankings')
def rankings():
    """Rankings and leaderboards page"""
    # Weekly leaderboard
    weekly_rankings = db.session.query(WeeklyRanking, User)\
        .join(User, WeeklyRanking.user_id == User.id)\
        .order_by(WeeklyRanking.points_earned.desc())\
        .limit(50).all()
    
    # Monthly leaderboard
    monthly_rankings = db.session.query(MonthlyRanking, User)\
        .join(User, MonthlyRanking.user_id == User.id)\
        .order_by(MonthlyRanking.points_earned.desc())\
        .limit(50).all()
    
    # All-time top users
    top_users = User.query.filter_by(is_active=True)\
        .order_by(User.total_points.desc())\
        .limit(50).all()
    
    return render_template('rankings.html', 
                         weekly_rankings=weekly_rankings,
                         monthly_rankings=monthly_rankings,
                         top_users=top_users)

# Referral System
@app.route('/referrals')
@login_required
def referrals():
    """User referral system page"""
    user_referral = Referral.query.filter_by(referrer_id=current_user.id).first()
    
    if not user_referral:
        # Create referral code for user
        referral_code = generate_referral_code(current_user.id)
        user_referral = Referral(
            referrer_id=current_user.id,
            referral_code=referral_code
        )
        db.session.add(user_referral)
        db.session.commit()
    
    # Get referred users
    referred_users = User.query.filter_by(referred_by_id=current_user.id).all()
    
    return render_template('referrals.html', 
                         referral=user_referral,
                         referred_users=referred_users)

# Course System Routes
@app.route('/courses')
def courses():
    """Course catalog page"""
    category = request.args.get('category', '')
    difficulty = request.args.get('difficulty', '')
    
    query = Course.query
    
    if category:
        query = query.filter(Course.category.ilike(f'%{category}%'))
    if difficulty:
        query = query.filter(Course.difficulty_level == difficulty)
    
    courses = query.order_by(Course.created_at.desc()).all()
    categories = db.session.query(Course.category).distinct().all()
    
    return render_template('courses.html', 
                         courses=courses,
                         categories=[cat[0] for cat in categories],
                         selected_category=category,
                         selected_difficulty=difficulty)

@app.route('/course/<int:course_id>')
def course_detail(course_id):
    """Course detail page"""
    course = Course.query.get_or_404(course_id)
    videos = CourseVideo.query.filter_by(course_id=course_id)\
        .order_by(CourseVideo.order_index.asc()).all()
    
    enrollment = None
    if current_user.is_authenticated:
        enrollment = CourseEnrollment.query.filter_by(
            user_id=current_user.id,
            course_id=course_id
        ).first()
    
    return render_template('course_detail.html', 
                         course=course,
                         videos=videos,
                         enrollment=enrollment)

@app.route('/course/<int:course_id>/enroll', methods=['POST'])
@login_required
def enroll_course(course_id):
    """Enroll in a course"""
    course = Course.query.get_or_404(course_id)
    
    existing_enrollment = CourseEnrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()
    
    if existing_enrollment:
        flash('Ya estás inscrito en este curso.', 'info')
        return redirect(url_for('course_detail', course_id=course_id))
    
    # Check if user has enough Crolars for premium courses
    if course.is_premium and current_user.crolars < course.price_crolars:
        flash('No tienes suficientes Crolars para inscribirte en este curso premium.', 'error')
        return redirect(url_for('course_detail', course_id=course_id))
    
    # Create enrollment
    enrollment = CourseEnrollment(
        user_id=current_user.id,
        course_id=course_id
    )
    db.session.add(enrollment)
    
    # Deduct Crolars for premium courses
    if course.is_premium:
        current_user.spend_crolars(course.price_crolars)
    
    db.session.commit()
    
    # Create notification
    create_notification(
        current_user.id,
        'Inscripción exitosa',
        f'Te has inscrito exitosamente en el curso: {course.title}',
        'course_enrollment',
        reference_id=course_id,
        reference_type='course'
    )
    
    flash('Te has inscrito exitosamente en el curso.', 'success')
    return redirect(url_for('course_detail', course_id=course_id))


