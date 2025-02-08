from django.contrib.auth import get_user_model
from social_core.pipeline.partial import partial

User = get_user_model()

def get_avatar(backend, strategy, details, response, user=None, *args, **kwargs):
    """Get user's avatar from social provider"""
    if backend.name == 'facebook':
        url = f"https://graph.facebook.com/{response['id']}/picture?type=large"
        if user:
            user.avatar_url = url
            user.save()
    elif backend.name == 'google-oauth2':
        if response.get('picture'):
            url = response['picture']
            if user:
                user.avatar_url = url
                user.save()

def create_user(strategy, details, backend, user=None, *args, **kwargs):
    """Create user if not exists"""
    if user:
        return {'is_new': False}

    fields = {
        'username': details.get('username'),
        'email': details.get('email'),
        'first_name': details.get('first_name', ''),
        'last_name': details.get('last_name', ''),
    }

    if not fields['username']:
        fields['username'] = fields['email'].split('@')[0]

    return {
        'is_new': True,
        'user': strategy.create_user(**fields)
    }

@partial
def require_email(strategy, details, user=None, is_new=False, *args, **kwargs):
    """Require email for social auth"""
    if user and user.email:
        return

    elif is_new and not details.get('email'):
        email = strategy.request_data().get('email')
        if email:
            details['email'] = email
        else:
            return strategy.redirect(
                '/social/email?partial_token={}'.format(strategy.session_get('partial_pipeline_token'))
            ) 