from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    career = db.Column(db.String(100), nullable=True)
    university = db.Column(db.String(100), nullable=True)
    avatar_url = db.Column(db.String(200), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    crolars = db.Column(db.Integer, default=100)  # Virtual currency
    total_points = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Referral system
    referred_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Relationships
    notes = db.relationship('Note', backref='author', lazy=True, cascade='all, delete-orphan')
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy=True, cascade='all, delete-orphan')
    achievements = db.relationship('UserAchievement', backref='user', lazy=True, cascade='all, delete-orphan')
    missions_completed = db.relationship('UserMission', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def add_crolars(self, amount):
        self.crolars += amount
        self.total_points += amount
        db.session.commit()
    
    def spend_crolars(self, amount):
        if self.crolars >= amount:
            self.crolars -= amount
            db.session.commit()
            return True
        return False

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    subject = db.Column(db.String(100), nullable=False)
    career = db.Column(db.String(100), nullable=True)
    file_url = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # pdf, image, etc.
    thumbnail_url = db.Column(db.String(500), nullable=True)
    views = db.Column(db.Integer, default=0)
    downloads = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=True)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    comments = db.relationship('Comment', backref='note', lazy=True, cascade='all, delete-orphan')
    likes_rel = db.relationship('Like', backref='note', lazy=True, cascade='all, delete-orphan')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    post_type = db.Column(db.String(50), default='general')  # general, question, discussion
    subject = db.Column(db.String(100), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')
    likes_rel = db.relationship('Like', backref='post', lazy=True, cascade='all, delete-orphan')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'), nullable=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'), nullable=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='likes')

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(100), nullable=False)
    crolars_reward = db.Column(db.Integer, default=0)
    category = db.Column(db.String(50), nullable=False)  # academic, social, special
    
    # Relationships
    user_achievements = db.relationship('UserAchievement', backref='achievement', lazy=True)

class UserAchievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement.id'), nullable=False)

class Mission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    mission_type = db.Column(db.String(50), nullable=False)  # daily, weekly, special
    target_value = db.Column(db.Integer, default=1)
    crolars_reward = db.Column(db.Integer, default=10)
    is_active = db.Column(db.Boolean, default=True)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user_missions = db.relationship('UserMission', backref='mission', lazy=True)

class UserMission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    progress = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mission_id = db.Column(db.Integer, db.ForeignKey('mission.id'), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

class MarketplaceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price_crolars = db.Column(db.Integer, nullable=False)
    item_type = db.Column(db.String(50), nullable=False)  # digital, physical, service
    image_url = db.Column(db.String(500), nullable=True)
    stock = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    seller = db.relationship('User', backref='marketplace_items')

# AI Chatbot Conversations
class ChatConversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='chat_conversations')
    messages = db.relationship('ChatMessage', backref='conversation', lazy=True, cascade='all, delete-orphan')

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    is_user_message = db.Column(db.Boolean, default=True)  # True for user, False for AI
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    conversation_id = db.Column(db.Integer, db.ForeignKey('chat_conversation.id'), nullable=False)

# Referral System
class Referral(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    referral_code = db.Column(db.String(20), unique=True, nullable=False)
    uses_count = db.Column(db.Integer, default=0)
    crolars_earned = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    referrer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    referrer = db.relationship('User', foreign_keys=[referrer_id], backref='referrals_created')

# Notifications
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # achievement, mission, message, like, comment, etc.
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Optional reference fields for linking to specific content
    reference_id = db.Column(db.Integer, nullable=True)  # ID of related content (post, note, etc.)
    reference_type = db.Column(db.String(50), nullable=True)  # type of related content
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='notifications')

# Enhanced User Missions with progress tracking
class DailyStreak(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_login_date = db.Column(db.Date, nullable=True)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='daily_streak', uselist=False)

# YouTube Course Integration
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    thumbnail_url = db.Column(db.String(500), nullable=True)
    difficulty_level = db.Column(db.String(50), default='beginner')  # beginner, intermediate, advanced
    category = db.Column(db.String(100), nullable=False)
    is_premium = db.Column(db.Boolean, default=False)
    price_crolars = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    instructor = db.relationship('User', backref='courses_created')
    videos = db.relationship('CourseVideo', backref='course', lazy=True, cascade='all, delete-orphan')
    enrollments = db.relationship('CourseEnrollment', backref='course', lazy=True)

class CourseVideo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    youtube_url = db.Column(db.String(500), nullable=False)
    duration_minutes = db.Column(db.Integer, default=0)
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

class CourseEnrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    progress_percentage = db.Column(db.Float, default=0.0)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='course_enrollments')

# Rankings and Leaderboards
class WeeklyRanking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    week_start = db.Column(db.Date, nullable=False)
    week_end = db.Column(db.Date, nullable=False)
    points_earned = db.Column(db.Integer, default=0)
    rank_position = db.Column(db.Integer, nullable=True)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='weekly_rankings')

class MonthlyRanking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, nullable=False)  # 1-12
    year = db.Column(db.Integer, nullable=False)
    points_earned = db.Column(db.Integer, default=0)
    rank_position = db.Column(db.Integer, nullable=True)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='monthly_rankings')
