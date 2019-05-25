from accounts.models import CelebModel, Profile
from django.utils.text import slugify
from django.contrib.auth import get_user_model


User = get_user_model()


def fuck_instagram(backend, strategy, details, response,
                   user, is_new, *args, **kwargs):
    if backend.name == 'instagram':
        print("\nFUCK YOU INSTAGRAM IN SETTINGS")
        print("RESPONSE", response)
        print("IS NEW?", is_new)
        print("KWARGS", kwargs)


def create_user(strategy, details, backend, user=None, *args, **kwargs):

    print("SOME SHIT", kwargs['response']['data'])

    USER_FIELDS = ['username', 'email']

    if user:
        return {'is_new': False}

    fields = dict((name, kwargs.get(name, details.get(name)))
                  for name in backend.setting('USER_FIELDS', USER_FIELDS))
    if not fields:
        return

    _user = kwargs['response']['data']

    fields.update({
        "username": _user['username'],
        "first_name": details['first_name'],
        "last_name": details['last_name'],
        "email": details['email']
    })

    instance = strategy.create_user(**fields)

    try:
        profile = instance.profile
        profile.fb_id = kwargs['uid']
        profile.slug = slugify(_user['username'])
        profile.profile_pic = _user['profile_picture']
        profile.bio = kwargs['bio'] if 'bio' in kwargs else '',
        profile.save()
    except Exception as e:
        import traceback
        errorLine = str(traceback.format_exc())
        print("UPDATE PROFILE ERROR", e, errorLine)
        pass

    data = {
        'is_new': True,
        'user': instance
    }

    return data


def link_profile(backend, strategy, details, response,
                 user, is_new, *args, **kwargs):
    if backend.name == 'instagram':
        user_data = response.get('data')
        if is_new:
            user.username = user_data['username']
            user.save()
        profile = user.profile

        influencer_data = {
            "profile": profile,
            "name": user_data['full_name'],
            "slug": slugify(user_data['username']),
            "ig_handle": user_data['username'],
            "link": f"https://www.instagram.com/{user_data['username']}",
            "followers": user_data['counts']['followed_by'],
            "profile_pic": user_data['profile_picture']
        }

        influencer, created = (
            CelebModel
            .objects
            .update_or_create(
                name=user_data['full_name'],
                ig_handle=user_data['username'],
                defaults=influencer_data,
            )
        )