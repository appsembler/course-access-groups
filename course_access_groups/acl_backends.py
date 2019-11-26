"""
Access Control backends to implement the Course Access Groups.
"""
import six


def dummy_backend(user, resource, default_has_access, options):  # pylint: disable=unused-argument
    """
    Access control backend to prevent users from loading the course `course-v1:Red+Red+Red2020`.

    Users with emails `@example.com` and `@appsembler.com` are being prevented, as long as they're logged in.
    """
    if six.text_type(resource.id) == 'course-v1:Red+Red+Red2020':
        if user.is_authenticated and (
            user.email.endswith('@example.com') or user.email.endswith('@appsembler.com')
        ):
            return False

    return default_has_access
