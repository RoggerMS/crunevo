import os
import cloudinary
import cloudinary.uploader
from flask import current_app
from datetime import datetime, timedelta

# Initialize Cloudinary
def init_cloudinary():
    cloudinary.config(
        cloud_name=current_app.config.get("CLOUDINARY_CLOUD_NAME"),
        api_key=current_app.config.get("CLOUDINARY_API_KEY"),
        api_secret=current_app.config.get("CLOUDINARY_API_SECRET")
    )

def upload_file_to_cloudinary(file, folder="crunevo"):
    """Upload file to Cloudinary and return URL and file type"""
    try:
        init_cloudinary()
        
        # Determine resource type based on file extension
        filename = file.filename.lower()
        if filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            resource_type = "image"
        elif filename.endswith('.pdf'):
            resource_type = "raw"
        else:
            resource_type = "auto"
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type=resource_type,
            use_filename=True,
            unique_filename=True
        )
        
        return {
            'url': result['secure_url'],
            'public_id': result['public_id'],
            'resource_type': resource_type,
            'format': result.get('format', ''),
            'bytes': result.get('bytes', 0)
        }
    except Exception as e:
        current_app.logger.error(f"Error uploading to Cloudinary: {str(e)}")
        return None

def get_file_type(filename):
    """Determine file type from filename"""
    extension = filename.lower().split('.')[-1]
    
    if extension in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
        return 'image'
    elif extension == 'pdf':
        return 'pdf'
    elif extension in ['doc', 'docx']:
        return 'document'
    else:
        return 'other'

def award_crolars(user, action_type):
    """Award Crolars to user based on action type"""
    from models import User
    from app import db
    
    crolars_rewards = {
        'upload_note': 20,
        'receive_like': 5,
        'comment': 3,
        'daily_login': 10,
        'complete_profile': 25,
        'first_note': 50,
        'helpful_comment': 10
    }
    
    reward = crolars_rewards.get(action_type, 0)
    if reward > 0:
        user.add_crolars(reward)
        return reward
    return 0

def check_achievements(user):
    """Check and award achievements to user"""
    from models import Achievement, UserAchievement, Note
    from app import db
    
    # Check for first note achievement
    if user.notes and len(user.notes) == 1:
        first_note_achievement = Achievement.query.filter_by(name="Primera Nota").first()
        if first_note_achievement:
            existing = UserAchievement.query.filter_by(
                user_id=user.id, 
                achievement_id=first_note_achievement.id
            ).first()
            if not existing:
                new_achievement = UserAchievement(
                    user_id=user.id,
                    achievement_id=first_note_achievement.id
                )
                db.session.add(new_achievement)
                user.add_crolars(first_note_achievement.crolars_reward)
    
    db.session.commit()

def create_default_achievements():
    """Create default achievements in the database"""
    from models import Achievement
    from app import db
    
    default_achievements = [
        {
            'name': 'Primera Nota',
            'description': 'Subiste tu primera nota de estudio',
            'icon': 'trophy',
            'crolars_reward': 50,
            'category': 'academic'
        },
        {
            'name': 'Colaborador',
            'description': 'Recibiste 10 likes en tus notas',
            'icon': 'heart',
            'crolars_reward': 100,
            'category': 'social'
        },
        {
            'name': 'Experto',
            'description': 'Subiste 10 notas de estudio',
            'icon': 'star',
            'crolars_reward': 200,
            'category': 'academic'
        },
        {
            'name': 'Comunidad',
            'description': 'Hiciste 25 comentarios útiles',
            'icon': 'message-circle',
            'crolars_reward': 150,
            'category': 'social'
        }
    ]
    
    for achievement_data in default_achievements:
        existing = Achievement.query.filter_by(name=achievement_data['name']).first()
        if not existing:
            achievement = Achievement(**achievement_data)
            db.session.add(achievement)
    
    db.session.commit()

def create_default_missions():
    """Create default missions in the database"""
    from models import Mission
    from app import db
    
    default_missions = [
        {
            'title': 'Sube una nota',
            'description': 'Comparte conocimiento subiendo una nota de estudio',
            'mission_type': 'daily',
            'target_value': 1,
            'crolars_reward': 30,
            'is_active': True
        },
        {
            'title': 'Haz 3 comentarios',
            'description': 'Participa en la comunidad haciendo comentarios útiles',
            'mission_type': 'daily',
            'target_value': 3,
            'crolars_reward': 20,
            'is_active': True
        },
        {
            'title': 'Recibe 5 likes',
            'description': 'Crea contenido que la comunidad valore',
            'mission_type': 'weekly',
            'target_value': 5,
            'crolars_reward': 50,
            'is_active': True
        }
    ]
    
    for mission_data in default_missions:
        existing = Mission.query.filter_by(title=mission_data['title']).first()
        if not existing:
            mission = Mission(**mission_data)
            db.session.add(mission)
    
    db.session.commit()

def format_time_ago(date):
    """Format datetime to show time ago"""
    now = datetime.utcnow()
    diff = now - date
    
    if diff.days > 7:
        return date.strftime('%d/%m/%Y')
    elif diff.days > 0:
        return f"hace {diff.days} día{'s' if diff.days > 1 else ''}"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"hace {hours} hora{'s' if hours > 1 else ''}"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"hace {minutes} minuto{'s' if minutes > 1 else ''}"
    else:
        return "hace un momento"

def generate_referral_code(user_id):
    """Generate unique referral code for user"""
    import random
    import string
    base_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"CRUN{user_id}{base_code}"

def create_notification(user_id, title, content, notification_type, reference_id=None, reference_type=None):
    """Create notification for user"""
    from models import Notification
    from app import db
    
    notification = Notification(
        user_id=user_id,
        title=title,
        content=content,
        notification_type=notification_type,
        reference_id=reference_id,
        reference_type=reference_type
    )
    db.session.add(notification)
    db.session.commit()
    return notification

def update_daily_streak(user):
    """Update user's daily login streak"""
    from models import DailyStreak
    from app import db
    from datetime import date, timedelta
    
    today = date.today()
    streak = DailyStreak.query.filter_by(user_id=user.id).first()
    
    if not streak:
        streak = DailyStreak(user_id=user.id)
        db.session.add(streak)
    
    if streak.last_login_date is None:
        streak.current_streak = 1
        streak.longest_streak = 1
        streak.last_login_date = today
    elif streak.last_login_date == today:
        return streak
    elif streak.last_login_date == today - timedelta(days=1):
        streak.current_streak += 1
        if streak.current_streak > streak.longest_streak:
            streak.longest_streak = streak.current_streak
        streak.last_login_date = today
    else:
        streak.current_streak = 1
        streak.last_login_date = today
    
    db.session.commit()
    
    if streak.current_streak >= 7:
        bonus = 50 + (streak.current_streak - 7) * 10
        user.add_crolars(bonus)
        create_notification(
            user.id,
            f"¡Racha de {streak.current_streak} días!",
            f"Has ganado {bonus} Crolars por tu racha de login consecutivo.",
            "streak_bonus"
        )
    
    return streak

def process_ai_response(user_message, conversation_id=None):
    """Process AI chatbot response using OpenAI"""
    import os
    
    try:
        import openai
        openai.api_key = os.environ.get('OPENAI_API_KEY')
        if not openai.api_key:
            raise ValueError("OpenAI API key not configured")
        
        system_prompt = """Eres Crunebot, un asistente educativo especializado en ayudar a estudiantes universitarios de Latinoamérica. 
        Responde de manera clara, educativa y amigable. Puedes ayudar con:
        - Explicaciones de conceptos académicos
        - Resolución de problemas de estudio
        - Organización de tiempo y técnicas de estudio
        - Recomendaciones de recursos educativos
        - Motivación y apoyo académico
        
        Mantén un tono profesional pero cercano, y siempre enfócate en el aspecto educativo."""
        
        client = openai.OpenAI(api_key=openai.api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return "Hola, soy Crunebot. Para poder ayudarte mejor, necesito que se configure la integración con OpenAI. Mientras tanto, puedes preguntarle a la comunidad en el foro académico."

def extract_youtube_id(url):
    """Extract YouTube video ID from URL"""
    import re
    patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
        r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None
