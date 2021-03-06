from django.contrib.auth.models import Group

import rules


# Called by boss-oidc to process JWT user roles
# This function should be in a separate module, but leaving it here for now
def assign_oidc_roles(user, roles):
    """Default implementation of the LOAD_USER_ROLES callback
    Args:
        user (UserModel): Django user object for the user logging in
        roles (list[str]): List of Keycloak roles assigned to the user
                           Note: Contains both realm roles and client roles
    """
    for role in roles:
        group, _ = Group.objects.get_or_create(name=f"{role}")
        user.groups.add(group)
        user.save()

# Delegate to keycloak in future iteration

# Predicates
@rules.predicate
def can_view_project(user, project):
    if not project:
        return False
    return rules.is_group_member(f'projman-{project.namespace}')(user)


@rules.predicate
def is_project_admin(user, project):
    if not project:
        return False
    return rules.is_group_member(f'projman-{project.namespace}-admin')(user)


@rules.predicate
def is_project_owner(user, project):
    if not project:
        return False
    return project.owner == user


@rules.predicate
def is_chart_owner(user, proj_chart):
    # Should have update rights on the parent project
    if not proj_chart:
        return False
    return user.has_perm('projman.change_project', proj_chart.project)


@rules.predicate
def can_view_chart(user, proj_chart):
    # Should have view rights on the parent project
    if not proj_chart:
        return False
    return user.has_perm('projman.view_project', proj_chart.project)


# Permissions
rules.add_perm('projman.view_project', is_project_owner | is_project_admin | rules.is_staff | can_view_project)
rules.add_perm('projman.add_project', rules.is_staff)
rules.add_perm('projman.change_project', is_project_owner | is_project_admin | rules.is_staff)
rules.add_perm('projman.delete_project', is_project_owner | is_project_admin | rules.is_staff)

rules.add_perm('projman.view_chart', is_chart_owner | rules.is_staff | can_view_chart)
rules.add_perm('projman.add_chart', is_project_owner | is_project_admin | rules.is_staff)
rules.add_perm('projman.change_chart', is_chart_owner | rules.is_staff)
rules.add_perm('projman.delete_chart', is_chart_owner | rules.is_staff)
